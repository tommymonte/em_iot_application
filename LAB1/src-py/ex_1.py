OFF_STATE = "Sleep"

def parse_info(file_path):
    # Dictionary to store the extracted information
    info_dict = {}

    # Open and read the file
    with open(file_path, 'r') as file:
        lines = file.readlines()
        Ptr = 0
        Ttr = 0
        
        # Loop through each line and parse based on pattern
        for line in lines:
            # Split based on ':', commonly used in key-value formats
            if ':' in line:
                name, value = line.split(':', 1)  # Split on the first colon
                if "State" in name:
                    if "State Run" in name:
                        name = "Pon"
                    elif "State "+OFF_STATE in name:
                        name = "Poff"
                    if name == "Poff" or name == "Pon" and "power" in value:
                        label, power = value.split('=', 1)  # Split on the first colon
                        power = power.strip()   
                        power = power[:-2]        # Remove any leading/trailing whitespace
                        info_dict[name] = float(power)         # Store in dictionary
                elif "Run -> "+OFF_STATE+" transition" in name:
                    if OFF_STATE in name:
                        if "energy" in value:
                            energy, time = value.split(',', 1)  # Split on the first colon
                            lab, val = energy.split('=', 1)  # Split on the first colon
                            val = val.strip()
                            en = float(val[:-2])
                            lab, val = time.split('=', 1)  # Split on the first colon
                            val = val.strip()
                            tm = float(val[:-2])
                            Ttr+= tm
                            Ptr+= en/tm
        
        info_dict["Ptr"] = float(Ptr)
        info_dict["Ttr"] = float(Ttr)
                            

    
    return info_dict

# Specify the path to your text file
file_path = '../dpm-simulator/result.txt'
# Parse and print extracted information
parsed_info = parse_info(file_path)
print(parsed_info)
print(str(parsed_info.get("Ttr")) +" + "+ str(parsed_info.get("Ttr")) +" * "+ str(parsed_info.get("Pon"))+" - "+str(parsed_info.get("Pon"))+" / "+str(parsed_info.get("Pon"))+" - "+str(parsed_info.get("Poff")))
Tbe = parsed_info.get("Ttr") + parsed_info.get("Ttr") * ((parsed_info.get("Pon")-parsed_info.get("Pon"))/(parsed_info.get("Pon")-parsed_info.get("Poff")))
print("Tbe is: "+str(Tbe))

