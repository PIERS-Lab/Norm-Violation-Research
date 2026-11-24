echo "Demo Configuration 2(Left)!"
echo "Verbose1"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d22
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r22
wait

echo "Ceasar"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d33
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r33
wait

echo "Base1"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d21
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r21
wait

echo "Binary(Task appropriation, offender)"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d23
wait   
ros2 launch nvr_arm_control deliver.launch.py config:=d12
wait  
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r23
wait
ros2 launch nvr_arm_control deliver.launch.py config:=r12
wait

echo "Misorder"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d11
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r11
wait