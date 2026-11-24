echo "testing all tajectories!"
echo "object 1 and goal 1"
ros2 launch nvr_arm_control deliver.launch.py config:=d11
wait   
ros2 launch nvr_arm_control deliver.launch.py config:=r11
wait
read -p "Press anything to continue"
echo "object 1 and goal 2"
ros2 launch nvr_arm_control deliver.launch.py config:=d12
wait
ros2 launch nvr_arm_control deliver.launch.py config:=r12
wait
read -p "Press enter to continue..." 
echo "object 1 and goal 3"
ros2 launch nvr_arm_control deliver.launch.py config:=d13
wait
ros2 launch nvr_arm_control deliver.launch.py config:=r13
wait
read -n 1 -s -r -p "Press anything to continue"

echo "object 2 and goal 1"
ros2 launch nvr_arm_control deliver.launch.py config:=d21
wait
ros2 launch nvr_arm_control deliver.launch.py config:=r21
wait
read -n 1 -s -r -p "Press anything to continue"
echo "object 2 and goal 2"
ros2 launch nvr_arm_control deliver.launch.py config:=d22
wait
ros2 launch nvr_arm_control deliver.launch.py config:=r22
wait
read -p "Press enter to continue..." 
echo "object 2 and goal 3"
ros2 launch nvr_arm_control deliver.launch.py config:=d23
wait
ros2 launch nvr_arm_control deliver.launch.py config:=r23
wait
read -n 1 -s -r -p "Press anything to continue"

echo "object 3 and goal 1"
ros2 launch nvr_arm_control deliver.launch.py config:=d31
wait
ros2 launch nvr_arm_control deliver.launch.py config:=r31
wait
read -n 1 -s -r -p "Press anything to continue"
echo "object 3 and goal 2"
ros2 launch nvr_arm_control deliver.launch.py config:=d32
wait
ros2 launch nvr_arm_control deliver.launch.py config:=r32
wait
read -n 1 -s -r -p "Press anything to continue"
echo "object 3 and goal 3"
ros2 launch nvr_arm_control deliver.launch.py config:=d33
wait
ros2 launch nvr_arm_control deliver.launch.py config:=r33
wait
echo "all done!"


