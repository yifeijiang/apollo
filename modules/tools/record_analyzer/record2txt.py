#!/usr/bin/env python

###############################################################################
# Copyright 2018 The Apollo Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

import sys
import argparse
import matplotlib.pyplot as plt
from cyber_py.record import RecordReader
from modules.control.proto import control_cmd_pb2
from modules.planning.proto import planning_pb2
from modules.canbus.proto import chassis_pb2
from modules.drivers.proto import pointcloud_pb2
from module_control_analyzer import ControlAnalyzer
from module_planning_analyzer import PlannigAnalyzer
from modules.perception.proto import perception_obstacle_pb2
from modules.prediction.proto import prediction_obstacle_pb2
from lidar_endtoend_analyzer import LidarEndToEndAnalyzer


def process(control_analyzer, planning_analyzer, lidar_endtoend_analyzer,
            is_simulation, plot_planning_path, plot_planning_refpath, all_data):
    is_auto_drive = False

    for msg in reader.read_messages():
        if msg.topic == "/apollo/canbus/chassis":
            chassis = chassis_pb2.Chassis()
            chassis.ParseFromString(msg.message)
            if chassis.driving_mode == \
                    chassis_pb2.Chassis.COMPLETE_AUTO_DRIVE:
                is_auto_drive = True
            else:
                is_auto_drive = False

        
            if (not is_auto_drive and not all_data) or \
                is_simulation or plot_planning_path or plot_planning_refpath:
                continue
            control_cmd = control_cmd_pb2.ControlCommand()
            control_cmd.ParseFromString(msg.message)
            control_analyzer.put(control_cmd)
            lidar_endtoend_analyzer.put_control(control_cmd)

        if msg.topic == "/apollo/planning":
            if (not is_auto_drive) and (not all_data):
                continue
            adc_trajectory = planning_pb2.ADCTrajectory()
            adc_trajectory.ParseFromString(msg.message)
            planning_analyzer.put(adc_trajectory)
            lidar_endtoend_analyzer.put_planning(adc_trajectory)

            if plot_planning_path:
                planning_analyzer.plot_path(plt, adc_trajectory)
            if plot_planning_refpath:
                planning_analyzer.plot_refpath(plt, adc_trajectory)

        if msg.topic == "/apollo/sensor/velodyne64/compensator/PointCloud2" or \
            msg.topic == "/apollo/sensor/lidar128/compensator/PointCloud2":
            if ((not is_auto_drive) and (not all_data)) or is_simulation or \
                plot_planning_path or plot_planning_refpath:
                continue
            point_cloud = pointcloud_pb2.PointCloud()
            point_cloud.ParseFromString(msg.message)
            lidar_endtoend_analyzer.put_lidar(point_cloud)

        if msg.topic == "/apollo/perception/obstacles":
            if ((not is_auto_drive) and (not all_data)) or is_simulation or \
                plot_planning_path or plot_planning_refpath:
                continue
            perception = perception_obstacle_pb2.PerceptionObstacles()
            perception.ParseFromString(msg.message)

        if msg.topic == "/apollo/prediction":
            if ((not is_auto_drive) and (not all_data)) or is_simulation or \
                plot_planning_path or plot_planning_refpath:
                continue
            prediction = prediction_obstacle_pb2.PredictionObstacles()
            prediction.ParseFromString(msg.message)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "usage: python main.py record_file"
    fn = sys.argv[1]
    reader = RecordReader(fn)
    for msg in reader.read_messages():
        if msg.topic == "/apollo/planning":
            adc_trajectory = planning_pb2.ADCTrajectory()
            adc_trajectory.ParseFromString(msg.message)
            fo = "planning_" + str(int(adc_trajectory.header.timestamp_sec * 1000)) 

            with open(fo + ".txt", 'w') as f:
                f.write(str(adc_trajectory))
            
            with open(fo + ".bin", 'wb') as f:
                f.write(adc_trajectory.SerializeToString())
        if msg.topic == "/apollo/control":
            pass
        if msg.topic == "/apollo/canbus/chassis":
            chassis = chassis_pb2.Chassis()
            chassis.ParseFromString(msg.message)
            fo = "chassis_" + str(int(chassis.header.timestamp_sec * 1000)) 

            with open(fo + ".txt", 'w') as f:
                f.write(str(chassis))
            
            with open(fo + ".bin", 'wb') as f:
                f.write(chassis.SerializeToString())
