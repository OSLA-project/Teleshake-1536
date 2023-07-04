@echo off

set TARGET_FOLDER=.\src\sila2_driver\thermoscientific\teleshake1536\generated\

set XML1=.\feature_xml\CancelController-v1_0.sila.xml
set XML2=.\feature_xml\settings.sila.xml
set XML3=.\feature_xml\shakecontroller.sila.xml
set XML4=.\feature_xml\SimulationController-v1_0.sila.xml

@echo #Generating Sila2 dependencies
@echo Target folder: %TARGET_FOLDER%

sila2-codegen.exe generate-feature-files -o %TARGET_FOLDER% %XML1% %XML2% %XML3% %XML4%