echo "Demo Configuration 1(Right)!"
echo "Verbose"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d31
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r31
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
ros2 launch nvr_arm_control deliver.launch.py config:=d21
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r21
wait

echo "Misorder"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d22
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r22
wait

echo "Braille (task-based appropriation)" 
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d21   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r21
