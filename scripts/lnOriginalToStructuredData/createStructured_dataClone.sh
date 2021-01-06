# Create empty but parallel structured_data dir.
# Start from scripts/lists/
rm -rf structured_data; mkdir structured_data ; cd structured_data ; xargs mkdir < ../struct_dataEmptyTree.txt; . ../touchStruct_dataFiles.sh; cd ..
