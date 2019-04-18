# Copyright 2018 The Reallusion Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import math, RLPy

from PySide2 import QtWidgets
from PySide2.shiboken2 import wrapInstance

#timer event init
rl_py_timer = None
timer_callback = None

#main widget
jcm_manager_dlg = None

#get avatar 
avatar = RLPy.RScene.FindObject(RLPy.EObjectType_Avatar, "Motion_Dummy_Female")

#get avatar bone and morph list
skeleton_bones = avatar.GetSkeletonComponent().GetSkinBones()
motion_bones = avatar.GetSkeletonComponent().GetMotionBones()
morph_component = avatar.GetMorphComponent()


class RLPyTimerCallback(RLPy.RPyTimerCallback):
    def __init__(self):
        RLPy.RPyTimerCallback.__init__(self)
        self.time_timeout_func = None
        
    def Timeout(self):
        self.time_timeout_func()
        
    def register_time_out(self, func):
        self.time_timeout_func = func
        
def update_skeleton():
    global skeleton_bones
    global morph_component
    for bone in skeleton_bones:
        #get bone name
        bone_name = bone.GetName()
        #get bone rotation
        result_xyz =bone.LocalTransform().R().ToRotationMatrix().ToEulerAngle(0,0,0,0)
        #convert radiance to degree
        angle_x = result_xyz[0]*180/math.pi
        angle_y = result_xyz[1]*180/math.pi
        angle_z = result_xyz[2]*180/math.pi
        if ( bone_name == "CC_Base_L_Forearm" ):
            #add morph key
            morph_component.AddKey("Motion_Dummy_Female","001_left_biceps_brachii_muscle", RLPy.RGlobal.GetTime(),angle_x/90, False, False)
        elif ( bone_name == "CC_Base_R_Forearm" ):
            morph_component.AddKey("Motion_Dummy_Female","002_right_biceps_brachii_muscle", RLPy.RGlobal.GetTime(),angle_x/90, False, False)
        elif ( bone_name == "CC_Base_L_Upperarm" ):
            morph_component.AddKey("Motion_Dummy_Female","003_left_deltoid_muscle", RLPy.RGlobal.GetTime(),1-angle_z/90, False, False)
        elif ( bone_name == "CC_Base_R_Upperarm" ):
            morph_component.AddKey("Motion_Dummy_Female","004_right_deltoid_muscle", RLPy.RGlobal.GetTime(),1-angle_z/90, False, False)
        else:
            pass
        
class JcmWidget(QtWidgets.QWidget):
    global rl_py_timer
    global timer_callback
    def __init__(self):
        super().__init__()
        self.label = QtWidgets.QLabel()
        self.label.setText("")
        #add two push buttons
        self.button_apply = QtWidgets.QPushButton("Apply Joint Morph Connection")
        self.button_cancel = QtWidgets.QPushButton("Cancel")
        #set vertical layout
        self.layout = QtWidgets.QVBoxLayout()
        #add buttons to main widget
        self.layout.addWidget(self.button_apply)
        self.layout.addWidget(self.button_cancel)
        #assign layout to main widget
        self.setLayout(self.layout)
        #bind functions to buttons
        self.button_apply.clicked.connect(self.apply)
        self.button_cancel.clicked.connect(self.cancel)
        
    def apply(self):
        #start timer event
        rl_py_timer.Start()
        
    def cancel(self):
        #stop timer event
        rl_py_timer.Stop()
        global morph_component
        #delete all morph keys
        morph_component.RemoveAllKeys("Motion_Dummy_Female", "001_left_biceps_brachii_muscle")
        morph_component.RemoveAllKeys("Motion_Dummy_Female", "002_right_biceps_brachii_muscle")
        morph_component.RemoveAllKeys("Motion_Dummy_Female", "003_left_deltoid_muscle")
        morph_component.RemoveAllKeys("Motion_Dummy_Female", "004_right_deltoid_muscle")
        
def run_script():
    global rl_py_timer
    global timer_callback
    #init timer event
    rl_py_timer = RLPy.RPyTimer()
    rl_py_timer.SetInterval( 100 )
    timer_callback = RLPyTimerCallback()
    rl_py_timer.RegisterPyTimerCallback(timer_callback) 
    timer_callback.register_time_out(update_skeleton)
    
    global jcm_manager_dlg
    jcm_manager_widget = JcmWidget()
    
    label = QtWidgets.QLabel()
    label.setText("Morph Targets are defined within the script and Morph Creator.")
    
    #create RDialog
    jcm_manager_dlg = RLPy.RUi.CreateRDialog()
    jcm_manager_dlg.SetWindowTitle("Joint Driven Morph")
    #wrap RDialog to Pyside Dialog
    main_pyside_dlg = wrapInstance(int(jcm_manager_dlg.GetWindow()), QtWidgets.QDialog)
    main_pyside_layout = main_pyside_dlg.layout()
    
    main_pyside_layout.addWidget(label)
    main_pyside_layout.addWidget(jcm_manager_widget)
    main_pyside_dlg.setFixedWidth(400)
    #show dialog
    jcm_manager_dlg.Show()
    
    
    
