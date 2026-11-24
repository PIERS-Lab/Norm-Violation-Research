echo "Demo Configuration 1(left)!"
echo "Base"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d32
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r32
wait

echo "Combo"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d23
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r23
wait

echo "Spatial"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d23
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r23
wait

echo "Cryptic"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d21
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r21
wait

echo "misorder1 (Tangible Violation)" 
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d12
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r12
wait