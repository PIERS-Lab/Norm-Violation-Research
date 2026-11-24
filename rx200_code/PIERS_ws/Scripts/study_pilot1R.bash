echo "Demo Configuration 1(Right)!"
echo "Base"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d21
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r21
wait

echo "Combo"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d11
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r11
wait

echo "Spatial"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d12
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r12
wait

echo "Binary (doing tangible appropriation)"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d23
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r23
wait

echo "Misorder"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d22
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r22
wait
