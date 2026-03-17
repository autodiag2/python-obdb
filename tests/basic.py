import obdb
import obd
import sys

if __name__ == "__main__":

    device_location = "/dev/ttys000"
    if 1 < len(sys.argv):
        device_location = sys.argv[1]
    
    connection = obd.OBD(portstr=device_location)

    response = connection.query(obdb.commands.Acura_TLX.TLX_GENERATOR, force=True)
    print(response.value)

    response = connection.query(obdb.commands.SAEJ1979.MIL, force=True)
    print(response.value)

    response = connection.query(obdb.commands.SAEJ1979.VSS, force=True)
    print(response.value)