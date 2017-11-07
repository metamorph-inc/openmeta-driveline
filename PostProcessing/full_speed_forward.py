import sys
import os
from common import PostProcess, update_metrics_in_report_json
from common import read_limits, check_limits_and_add_to_report_json


if __name__ == '__main__':
    try:
        mat_file_name = sys.argv[1]
        if not os.path.exists(mat_file_name):
            print 'Given result file does not exist: {0}'.format(sys.argv[1])
            os._exit(3)

        ## First limit part
        limit_dict, filter = read_limits()
        ## End of first limit part
        
        ## Post processing part
        filter.append('road_Wheel_Load_Both_Sides.vehicleSpeed')
        filter.append('road_Wheel_Load_Both_Sides.Accel_20kph')
        filter.append('road_Wheel_Load_Both_Sides.Accel_40kph')
        filter.append('design.tank_level')
        filter.append('design.FuelTankVolume')
        filter.append('driver_Land_Profile.driver_control.error_current.u2')
        
        # loads results with the filtered out variables (and 'time' which is default)
        pp = PostProcess(mat_file_name, filter)
        start_fraction = pp.get_data_by_time('design.tank_level', 0.01)[0]
        end_fraction = pp.last_value('design.tank_level')
        tank_volume = pp.last_value('design.FuelTankVolume')
        distance_covered_m = pp.integrate('driver_Land_Profile.driver_control.error_current.u2')
        
        print "distance_covered_m : {0}".format(distance_covered_m)
        print "end_time           : {0}".format(pp.time[-1])
        #pressure_variable_name = [var_name for var_name in filter if var_name.endswith('hot_fluid_out.p')][0]
        metrics = {}
        metrics.update({'FuelConsumed': {'value': (start_fraction - end_fraction) * tank_volume, 'unit': 'L'}})
        metrics.update({'VehicleSpeed': {'value': pp.global_max("road_Wheel_Load_Both_Sides.vehicleSpeed"), 'unit': 'kph'}})
        metrics.update({'AverageSpeed': {'value': (distance_covered_m / pp.time[-1]) * 3.6, 'unit': 'kph'}})
        metrics.update({'Acc20kph': {'value': pp.last_value('road_Wheel_Load_Both_Sides.Accel_20kph'), 'unit': 's'}})
        metrics.update({'Acc40kph': {'value': pp.last_value('road_Wheel_Load_Both_Sides.Accel_40kph'), 'unit': 's'}})
        
        #metrics.update({'EngineAirPressure': {'value': pp.last_value(pressure_variable_name), 'unit': 'Pascal'}})

        cwd = os.getcwd()
        os.chdir('..')
        print 'Plot saved to : {0}'.format(pp.save_as_svg('road_Wheel_Load_Both_Sides.vehicleSpeed', 
                                                          pp.global_abs_max("road_Wheel_Load_Both_Sides.vehicleSpeed"),
                                                          'VehicleSpeed',
                                                          'max(road_Wheel_Load_Both_Sides.vehicleSpeed)',
                                                          'kph'))
        print 'Plot saved to : {0}'.format(pp.save_as_svg('road_Wheel_Load_Both_Sides.Accel_20kph', 
                                                          pp.last_value('road_Wheel_Load_Both_Sides.Accel_20kph'),
                                                          'Acc20kph',
                                                          'last_value(road_Wheel_Load_Both_Sides.Accel_20kph)',
                                                          's'))
        print 'Plot saved to : {0}'.format(pp.save_as_svg('road_Wheel_Load_Both_Sides.Accel_40kph', 
                                                          pp.last_value('road_Wheel_Load_Both_Sides.Accel_40kph'),
                                                          'Acc40kph',
                                                          'last_value(road_Wheel_Load_Both_Sides.Accel_40kph)',
                                                          's'))
        update_metrics_in_report_json(metrics)
        ## end of postprocessing part

        ## Second limit part
        check_limits_and_add_to_report_json(pp, limit_dict)
        ## end of Second limit part
        os.chdir(cwd)
    except Exception as err:
        print err.message
        if os.name == 'nt':
            import win32api
            win32api.TerminateProcess(win32api.GetCurrentProcess(), 1)
        else:
            sys.exit(1)

