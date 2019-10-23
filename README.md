# TeamCityRestApiClientPython
This is a wrapper of TeamCity RESTful API client written by Python.

## Features
* Create a new project
* Copy build type
* Attach a template to a build type
* Detach the template from a build type
* Create a new build type
* Run (trigger) a build type
* Get all projects
* Get details of a build type
* Get parameters of a build type
* Update parameters of a build type

> The wrapper class requires requests (v2.22.0).
> If you don't have it yet, please install first.
> I don't think the specific version is required but the latest version should be ok unless they make massive changes.

```
pip install requests==2.22.0
```

## Sample
I hope the sample.py gives you an idea of how to use the wrapper.

## Last but not least
Any idea or comments to improve the wrapper would be appreciated.
