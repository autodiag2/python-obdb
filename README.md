# python-obdb
[python-OBD](https://github.com/brendan-w/python-OBD) extended command set with [OBDb repos](https://github.com/OBDb).

# Install
```bash
git clone --depth=1 https://github.com/autodiag2/python-obdb
cd python-obdb
pip install -e .
```

# Use
Check the [command set](/obdb/commands.py)  
  
For instance:
```python
import obdb
import obd
import sys

if __name__ == "__main__":

    device_location = "/dev/ttys000"
    if 1 < len(sys.argv):
        device_location = sys.argv[1]
    
    connection = obd.OBD(portstr=device_location)

    response = connection.query(obd.commands.SPEED)
    print("vehicle speed stock")
    print(response.value)

    response = connection.query(obdb.commands.SAEJ1979.VSS, force=True)
    print("vehicle speed custom")
    print(response.value)

    response = connection.query(obd.commands.RPM)
    print("engine speed stock")
    print(response.value)

    response = connection.query(obdb.commands.SAEJ1979.RPM, force=True)
    print("engine speed custom")
    print(response.value)

    response = connection.query(obdb.commands.Acura_TLX.TLX_GENERATOR, force=True)
    print("obdb.commands.Acura_TLX.TLX_GENERATOR")
    print(response.value)

    response = connection.query(obdb.commands.SAEJ1979.MIL, force=True)
    print("obdb.commands.SAEJ1979.MIL")
    print(response.value)
```