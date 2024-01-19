kubectl run mypod --image nginx --restart Never --dry-run=client -o yaml > mypod.yaml;

sleep 2; 
echo 'yaml file created';
echo 'Push file to the git repo';
git add mypod.yaml && git commit -m "pod added" && git push
