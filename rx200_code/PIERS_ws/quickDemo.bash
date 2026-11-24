echo "testing a couple of trajectories"
echo "moving obj1 to goal1 and back"
ros2 launch nvr_arm_control deliver.launch.py config:=d11
wait   
ros2 launch nvr_arm_control deliver.launch.py config:=r11
wait
echo "moving obj2 to goal2 and back "
ros2 launch nvr_arm_control deliver.launch.py config:=d22
wait   
ros2 launch nvr_arm_control deliver.launch.py config:=r22
wait
echo "moving obj3 to goal3 and back"
ros2 launch nvr_arm_control deliver.launch.py config:=d33
wait   
ros2 launch nvr_arm_control deliver.launch.py config:=r33
wait

echo done!
