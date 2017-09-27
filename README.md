if you wanna run the update_check
first, you should check the **straas-service file** in the dir
then
```
nohup python -u background.py > update.log 2>&1 &
```
It returns a pid:
just like
```
[1] 7820
```
If you wanna stop the process, for example, just need to input:
```
kill 7820
```

If you forgot the pid, try to input:
```
ps -e | grep python
```
according to the time the process maintain, you can get the pid you want


NO THANKS