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
        filter.append('design.tank_level')
        filter.append('design.FuelTankVolume')
        filter.append('design.engine_heat_port.T')
        filter.append('driver_Land_Profile.driver_control.error_current.u2')

        # loads results with the filtered out variables (and 'time' which is default)
        pp = PostProcess(mat_file_name, filter)
        metrics = {}
        start_fraction = pp.get_data_by_time('design.tank_level', 0.01)[0]
        end_fraction = pp.last_value('design.tank_level')
        tank_volume = pp.last_value('design.FuelTankVolume')
        distance_covered_m = pp.integrate('driver_Land_Profile.driver_control.error_current.u2')

        print "--- ==== Intermediate Metrics ==== ---"
        print "start_fraction      : {0}".format(start_fraction)
        print "end_fraction        : {0}".format(end_fraction)
        print "tank_volume         : {0}".format(tank_volume)
        print "distance_covered_m  : {0}".format(distance_covered_m)
        print "end_time            : {0}".format(pp.time[-1])

        VehicleSpeed = pp.global_max("road_Wheel_Load_Both_Sides.vehicleSpeed")
        Acc20kph = pp.last_value('road_Wheel_Load_Both_Sides.Accel_20kph')
        Acc40kph = pp.last_value('road_Wheel_Load_Both_Sides.Accel_40kph')
        AverageSpeed = (distance_covered_m / pp.time[-1]) * 3.6
        FuelConsumed = (start_fraction - end_fraction) * tank_volume
        EngineTemperature = pp.last_value('design.engine_heat_port.T') - 273.15
        ExhaustTemperature = pp.last_value("air_Path_For_Testing.temperature.T") - 273.15
        CoolantTemperature = pp.last_value("air_Path_For_Testing1.temperature.T") - 273.15

        print "--- ==== Metrics ==== ---"
        print "VehicleSpeed        : {0}".format(VehicleSpeed)
        print "Acc20kph            : {0}".format(Acc20kph)
        print "Acc40kph            : {0}".format(Acc40kph)
        print "AverageSpeed        : {0}".format(AverageSpeed)
        print "FuelConsumed        : {0}".format(FuelConsumed)
        print "EngineTemperature   : {0}".format(EngineTemperature)
        print "ExhaustTemperature  : {0}".format(ExhaustTemperature)
        print "CoolantTemperature  : {0}".format(CoolantTemperature)

        metrics.update({'VehicleSpeed': {'value': VehicleSpeed, 'unit': 'kph'}})
        metrics.update({'Acc20kph': {'value': Acc20kph, 'unit': 's'}})
        metrics.update({'Acc40kph': {'value': Acc40kph, 'unit': 's'}})
        metrics.update({'AverageSpeed': {'value': AverageSpeed, 'unit': 'kph'}})
        metrics.update({'FuelConsumed': {'value': FuelConsumed, 'unit': 'L'}})
        metrics.update({'EngineTemperature': {'value': EngineTemperature, 'unit': 'C'}})
        metrics.update({'ExhaustTemperature': {'value': ExhaustTemperature, 'unit': 'C'}})
        metrics.update({'CoolantTemperature': {'value': CoolantTemperature, 'unit': 'C'}})

        cwd = os.getcwd()
        os.chdir('..')
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

