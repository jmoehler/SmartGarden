# Testing Strategy

In this project we meticulously tested various components, including the sensors/actuators, a webserver, a database, the communication protocol between the hub and sensors/actuators, picture analysis, and the autocontroller. The testing approach incorporated multiple stages and measures to ensure the robustness and functionality of the code.

Initially, the developer (of the specific feature/resdesign/etc.) actively tested the code, addressing any issues. Subsequently, merge requests underwent thorough review, with approval granted only if the code ran successfully. For most features, especially in the later stages, we employed integration tests through the webpage. Any anomalies detected in the webserver triggered a comprehensive bug hunt across different layers of the system, such as faulty communication protocols or database errors.

During the early development of the communication protocol/API, we extensively tested it using Postman. Postman continued to be a valuable tool in later stages for isolated tests, particularly when the communication protocol was updated or to verify the proper functioning of specific components like pumps and LEDs.

Our database underwent several refinements, reaching its current state with features like argument type and semantic checking, robust error handling, and other improvements. Manual testing of the webserver over the webpage was conducted, and nearly all components underwent parallel testing through this method.

To ensure the autocontrollers reliability, we conducted manual tests to verify correct actions when values were out of range. An extensive log system was implemented, streamlining bug tracking. Although unit testing was part of our strategy, the primary emphasis was on manual testing, particularly over the webpage, involving multiple individuals due to the collaborative nature of merge requests.





