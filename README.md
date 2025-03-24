# Energy-Efficient Systems and Power Management

## Authors

- Tommaso Montedoro
- Fabio Delbosco

## Project Overview

This project explores energy-efficient methodologies in different contexts, including dynamic power management, display power optimization, and energy storage/conversion for IoT devices. The project is structured into three main labs, each addressing a specific aspect of energy efficiency.

---

## Lab 1: Dynamic Power Management (DPM)

### Objective

- Implement and analyze power management policies to optimize energy consumption in embedded systems.

### Work Performed

- Developed a power state machine (PSM) simulator in C.
- Tested different power management policies:
  - **Timeout Policy**: Transitions to low-power states after a predefined inactivity period.
  - **Predictive Policy**: Uses history-based prediction to determine the optimal low-power state.
- Evaluated the impact of different workloads and power state transitions on energy efficiency.
- Conducted comparative analysis to determine the best policy for given scenarios.

---

## Lab 2: Energy-Efficient Displays

### Objective

- Explore methods to reduce power consumption in OLED displays through image processing techniques.

### Work Performed

- Implemented image manipulation techniques in Python to optimize power usage:
  - **Color Transformation**: Adjusted pixel colors while maintaining image quality.
  - **Histogram Equalization**: Modified image contrast to achieve power savings.
  - **Dynamic Voltage Scaling (DVS)**: Reduced supply voltage while applying compensation techniques.
- Evaluated trade-offs between power savings and image distortion.
- Conducted an in-depth analysis to determine the optimal trade-off point for energy efficiency.

---

## Lab 3: Energy Storage, Generation, and Conversion

### Objective

- Model and simulate an IoT device with energy storage, power generation, and conversion systems.

### Work Performed

- Designed and simulated an IoT system with components including:
  - **Sensors** (Temperature, Air Quality, Methane, and Microphone)
  - **Memory and Control Unit (MCU)**
  - **RF Transmission Module (ZigBee Protocol)**
  - **Thin-film Photovoltaic (PV) Module with DC-DC Converter**
  - **Lithium-Ion Battery System**
- Developed models for energy conversion and storage using SystemC/SystemC-AMS.
- Simulated system performance under different power loads and energy sources.
- Analyzed energy flow, power efficiency, and battery lifetime under varying conditions.

---

## Conclusion

This project demonstrates key strategies for energy efficiency in embedded systems, display technology, and IoT power management. By applying these methodologies, we can optimize energy consumption, enhance device lifetime, and improve overall system efficiency.

---

## Requirements

- **Lab 1**: C, MATLAB, Python (for data analysis)
- **Lab 2**: Python, OpenCV, scikit-image
- **Lab 3**: C++ Compiler, SystemC, SystemC-AMS

## Acknowledgments

Special thanks to the course instructors and colleagues for valuable insights and guidance throughout the project.


