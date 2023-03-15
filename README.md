# The `spc-io` package

`spc-io` provides a Input/Output interface to `spc` file format.

`spc-io` supports:
- Only LSB file format
- Both single and double precision
- Supports float, int16 and int 32 data types regarding `fexp` and `subexp` fields
- 4D structures. `w` and `z` can be incremental or arbitrary
- global X and local X array (all variations of `TMULTI`, `TXVALS`, `TXYXYS`, `TORDRD`)

There are two levels of abstraction:
- low_level is built with `ctypes.Structure`s that parse the header and data from spc;
- high_level is more user friendly way to access data that does not contain technical details.

## How to use

### High-level structures

#### Read from file

```python
import spc_io
spc_file_name = 'some_file.spc'
with open(spc_file_name, 'br') as f:
    spc = spc_io.SPC.from_bytes_io(f)
```

#### Export to `pandas.DataFrame`

```python
df_table = spc.to_dataframe_table()  # only possible when a global X axis is used (e.g. TXYXYS=0)
df_flat = spc.to_dataframe_flattened()  # always possible
```

#### Access log-book

```python
logbook_binary = spc.log_book.binary
logbook_disk = spc.log_book.disk
logbook_text = spc.log_book.text
```

#### Iterate over subfiles

```python
for sub in spc:
    xarray = sub.xarray
    yarray = sub.yarray
    w = sub.w
    z = sub.z
    # do something with `xarray`, `yarray`, `w` and `z`
```

or

```python
for sub_i in range(len(spc)):
    xarray = spc[sub_i].xarray
    yarray = spc[sub_i].yarray
    w = spc[sub_i].w
    z = spc[sub_i].z
    # do something with `xarray`, `yarray`, `w` and `z`
```

#### Design `SPC` manually and export

```python
import spc_io.high_level as spc_high
import numpy as np
spc = spc_high.SPC(xarray=spc_high.EvenAxis(1, 10, 100))
for z in [100, 200, 300]:
    for w in [1,2,3]:
        spc.add_subfile(yarray=np.random.uniform(size=100)+w+z, w=w, z=z)
df = spc.to_dataframe_table()
```

#### Use `find_wz()`

```python
for w in spc.warray:
    for z in spc.zarray:
        subfile = spc.find_wz(w, z)
        # do something with subfile:
        # subfile.xarray, subfile.yarray, subfile.w(==w) , subfile.z(==z)
```

#### Export to a `spc` file

```python
spc_filname = 'non-existing.spc'
with open(spc_filename, 'wb') as f:
    f.write(spc.to_spc_raw().to_bytes())
```


### Low-level structures

For some specific tasks or debugging low-level structures might be helpful

#### Read SpcRaw from file

```python
import spc_io
spc_file_name = 'some_file.spc'
with open(spc_file_name, 'br') as f:
    spcraw = spc_io.SpcRaw.from_bytes_io(f)
```

#### Access header fields

```python
if spcraw.main_header.ftflgs.TMULTI:
    print('multiple subfiles')
    if spcraw.main_header.ftflgs.TXYXYS:
        print('individual xarrays for each subfile')

for sub in spcraw.subs:
    print(f'subfile number {sub.header.subindx} has subexp={sub.header.subexp}')
    print(sub.yarray)
```


## Some other examples

### `spc[0].xarray is spc.xarray` when `TXYXYX=0`

```python
import spc_io.high_level as spc_high
import numpy as np
spc = spc_high.SPC(xarray=spc_high.EvenAxis(1, 10, 100))
spc.add_subfile(yarray=np.random.uniform(size=100))
assert spc.xarray is spc[0].xarray
```

## Acknowledgements

🇪🇺 This project has received funding from the European Union’s Horizon 2020 research and innovation program under [grant agreement No. 952921](https://cordis.europa.eu/project/id/952921).
