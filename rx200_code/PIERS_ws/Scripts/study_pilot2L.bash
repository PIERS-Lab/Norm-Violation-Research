echo "Demo Configuration 1(Left)!"
echo "Verbose"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d23
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r23
wait

echo "Ceasar"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d33
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r33
wait

echo "Base"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d32
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r32
wait

echo "Misorder"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d11
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r11
wait

echo "Braille (task-based appropriation)" 
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d33
wait
ros2 launch nvr_arm_control deliver.launch.py config:=d21
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r33
wait
ros2 launch nvr_arm_control deliver.launch.py config:=r21
wait
