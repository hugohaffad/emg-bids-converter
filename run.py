
# Create new dataset
uv run emg-bids init ../../my_dataset --name "ISCUM" --author "H. Haffad" --license CC-BY-4.0

# Add new participants
uv run emg-bids add ../../my_dataset "K:\datasets\ISCUM\S_01\S_01_mvc1.otb4" --subject 01 --task mvc --run 1 --emg-reference "patella"
uv run emg-bids add ../../my_dataset "K:\datasets\ISCUM\S_01\S_01_mvc2.otb4" --subject 01 --task mvc --run 2 --emg-reference "patella"

# Validate the dataset against BIDS specification
bids-validator ..\..\my_dataset