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
        filter.append('air_Path_For_Testing.temperature.T')
        filter.append('air_Path_For_Testing1.temperature.T')

        pp = PostProcess(mat_file_name, filter)

        metrics = {}
        metrics.update({'VehicleSpeed': {'value': pp.global_max("road_Wheel_Load_Both_Sides.vehicleSpeed"), 'unit': 'kph'}})
        metrics.update({'ExhaustTemperature': {'value': pp.last_value("air_Path_For_Testing.temperature.T") - 273.15, 'unit': 'C'}})
        metrics.update({'CoolantTemperature': {'value': pp.last_value("air_Path_For_Testing1.temperature.T") - 273.15, 'unit': 'C'}})
        metrics.update({'Acc20kph': {'value': pp.last_value('road_Wheel_Load_Both_Sides.Accel_20kph'), 'unit': 's'}})

        cwd = os.getcwd()
        os.chdir('..')
        print 'Plot saved to : {0}'.format(pp.save_as_svg('road_Wheel_Load_Both_Sides.vehicleSpeed',
                                                          pp.global_abs_max("road_Wheel_Load_Both_Sides.vehicleSpeed"),
                                                          'VehicleSpeed',
                                                          'max(road_Wheel_Load_Both_Sides.vehicleSpeed)',
                                                          'kph'))
        print 'Plot saved to : {0}'.format(pp.save_as_svg('air_Path_For_Testing.temperature.T',
                                                          pp.last_value('air_Path_For_Testing.temperature.T'),
                                                          'ExhaustTemperature',
                                                          'last_value(air_Path_For_Testing.temperature.T)',
                                                          'K'))
        print 'Plot saved to : {0}'.format(pp.save_as_svg('air_Path_For_Testing1.temperature.T',
                                                          pp.last_value('air_Path_For_Testing1.temperature.T'),
                                                          'CoolantTemperature',
                                                          'last_value(air_Path_For_Testing1.temperature.T)',
                                                          'K'))
        print 'Plot saved to : {0}'.format(pp.save_as_svg('road_Wheel_Load_Both_Sides.Accel_20kph',
                                                          pp.last_value('road_Wheel_Load_Both_Sides.Accel_20kph'),
                                                          'Acc20kph',
                                                          'last_value(road_Wheel_Load_Both_Sides.Accel_20kph)',
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

