# Introduction
A lambda function takes care of the following events emitted by eventbridge and reciving from SNS:

1. ECS Container Instance State
2. ECS Task State

## ECS Container Instance State

For ECS Container Instance, it supports:

1. GPU online
2. GPU offline

## ECS Task State

Stopped task error codes have a category associated with them, for example "ResourceInitializationError". To get more information about each category, see the following:

1. TaskFailedToStart
2. ResourceInitializationError
3. ResourceNotFoundException	
4. InternalError
5. OutOfMemoryError
6. ContainerRuntimeError
7. ContainerRuntimeTimeoutError
8. CannotStartContainerError
9. CannotStopContainerError
10. CannotInspectContainerError
11. CannotCreateVolumeError
12. CannotPullContainer

Currently, only the ```TaskFailedToStart``` will lead to run_task.

# Deployment

TBD
