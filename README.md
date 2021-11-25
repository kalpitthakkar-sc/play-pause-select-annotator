# Simple annotator
Allows to play, pause and mark a frame number.
Can also seek to next and previous frame easily.

Controls:  
```
w = play  
x = reverse  
s = pause  
d = next frame  
a = previous frame  
z = reduce player fps by 5 (Min 5)  
c = increase player fps by 5 (Max 30)  
q = quit from annotation process  
f = load next video  
m = mark the frame (saved to annotation dir) 
```

How to use:  
* Once video is loaded in the window, you can play forward using `w` and reverse using `x`.
* If you see a frame or a part of video where you think there's a frame to choose, pause the video usin `s`.
* Now, you can move to the next and previous frame using `d` and `a`, respectively.
* To mark the current frame and choose it, press `m`. The frame will be saved to an output directory corresponding to the video.
* Once the current video is done, use `f` to load the next video. To quit the entire process, use `q`.