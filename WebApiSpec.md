# Introduction #

This is the api documentation for the REST interface to the Stampede loaded databases.
Here are some important notes:

  * All responses are in JSON and include "application/json" in the content-type header.
  * Invalid queries return a 404 with an English reason for failure.
  * The "timeCeiling" parameter is used to see the state of the system up until a certain time. Think of it as a snapshot of activity at a certain point.
  * You can currently access the mongo version of this API at http://awp.cs.usfca.edu/

# Syntax Key #
```
[]: an Array (or List)
{<key>:<value>}: a dictionary
<workflow_id>: The id of a specific workflow. Example: " 1degree_1nodes_skynet"
<job_id>: THe id of a specific job. Example: " mDiffFit_ID000067"
<stateType>: A process state. Examples: "submitted", "failed", "complete"
<time>: UTC Time string
<seconds>: integer of time in seconds
<int>: integer
<string>: string
<timestamp>: float, time since epoch
```

# Available URI's #
```
URI: /workflow/unique (alternative: /workflow/all)
Returns: [{"id":<workflow_id>, "state":<stateType>, "lastEvent":<timestamp>},...]
Options: timeCeiling: <timestamp>
         limit: <int>
         page: <int>
```

```
URI:/workflow/<workflow_id>
Returns: {"id":<workflow_id>,
          "state":<stateType>,
          "jobStatus": {"submitted":<int>,
                        "running":<int>,
                        "completed":<int>,
                        "failed":<int>
                       },
          "submitted":<time>,
          "runtime":<seconds>,
          "lastEvent":<timestamp> }
Options: timeCeiling: <timestamp>
```

```
URI:/workflow/<workflow_id>/jobs
Returns: [
          {"id":<workflow_id>, "state":<stateType>, "submitted":<time>, "runtime":<seconds>},
          ...
         ]
Options: timeCeiling: <timestamp>
         limit: <int>
         page: <int>
```

```
URI:/workflow/<workflow_id>/<job_id>
Returns: {"id":<workflow_id>, "state":<stateType>, "submitted":<time>, "runtime":<seconds>}
Options: timeCeiling: <timestamp>
```

```
URI:/workflow/<workflow_id>/<job_id>/parents
Returns: [<job_id>, ...]
Options: timeCeiling: <timestamp>
```

```
URI:/workflow/<workflow_id>/<job_id>/children
Returns: [<job_id>, ...]
Options: timeCeiling: <timestamp>
```


# Sample Queries #
## Get Workflow Data ##
URI: http://awp.cs.usfca.edu/workflow/164c08e1-094f-41bc-85b5-493bfadbd23a
Response:
```
{
    submitted: 1268163288
    lastEvent: 1268164295
    state: "IMAGE_SIZE"
    jobStatus: {
        failed: 0
        running: 0
        completed: 107
        submitted: 0
    }
    runtime: 1007
    id: "164c08e1-094f-41bc-85b5-493bfadbd23a"
}
```

## Get Data on 2 current workflows ##
URI: http://awp.cs.usfca.edu/workflow/all?limit=2
Response:
```
[
    {
      lastEvent: 1268164295
      state: "IMAGE_SIZE"
      id: "164c08e1-094f-41bc-85b5-493bfadbd23a"
    },
    {
      lastEvent: 1268164851
      state: "JOB_TERMINATED"
      id: "165bc398-b8c2-4bbd-bd52-05e84e2d2bfa"
    }

]
```

## Get workflow data at a particular snapshot in time ##
URI: http://awp.cs.usfca.edu/workflow/164c08e1-094f-41bc-85b5-493bfadbd23a?timeCeiling=1268163388
Response:
```
{
    submitted: 1268163288
    lastEvent: 1268163369
    state: "SUBMIT"
    jobStatus: {
        failed: 0
        running: 0
        completed: 2
        submitted: 20
    }
    runtime: 81
    id: "164c08e1-094f-41bc-85b5-493bfadbd23a"
}
```

## Get data for a particular job ##
URI: http://awp.cs.usfca.edu/workflow/164c08e1-094f-41bc-85b5-493bfadbd23a/merge_ligo-lalapps_coire-1.0_PID2_ID25
Response:
```
{
    state: "JOB_SUCCESS"
    runtime: 182
    id: "merge_ligo-lalapps_coire-1.0_PID2_ID25"
    submitted: 1268163501
}
```