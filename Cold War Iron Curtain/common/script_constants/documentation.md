# Constants
Constants are a way to define simple and complex script values
that are reusable in different files in the scripts.
Only entries that are documented to support these script constant
can utilize it.

All scoped variables can access script constants by using the `constant:` prefix.

Note that reloading the script database is not enough to propagate the constants.
The script that uses the constants has to be reloaded after the script constant database has been reloaded.

A script constant have the following format:

```python
category_name = {
    # Mandatory to be the first entry
    schema = {
        # specific name of the key mutually exclusive with any_key
        key = foobar 
        # Accept any key of alphabetic characters (no dots), mutually exclusive with key
        any_key = yes
        
        # The data sepecification
        data = int # integer
        data = fixed_point # floating point
        # or
        data = { SCHEMA_OBJECTS } # complex schema entry
    }

    # All the data entries that matches the specified schema.
    DATA*
}
```

# Examples
```python
sp_complexity = {
    schema = {
        any_key = yes
        data = {
            {
                key = min
                data = int
            }
            {
                key = max
                data = int
            }
        }
    }

    small = {
        min = 20
        max = 30
    }

    medium = {
        min = 15
        max = 20
    }

    large = {
        min = 10
        max = 15
    }

    insane = {
        min = 5
        max = 10
    }
}

sp_basic_research_time = {
    schema = {
        any_key = yes
        data = int
    }

    short = 15
    medium = 30
    long = 60
    very_long = 90
}
```