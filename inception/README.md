## I just want to use Inception...

Much of the dialogue surrounding the Google Inception model revolves around transfer learning, which is great, but what if I just want to use the original network? Surprisingly there doesn't seem to be as much written on using the orginal network, and what there is isn't as simple as it could be or should be. [Magnus Erik Hvass Pedersen](https://github.com/Hvass-Labs/TensorFlow-Tutorials) has a pretty good repo using the original Inception model. However, it still isn't as simple as it should be. I wrote Easy Inception, which is based on Magnus's code and my experience with transfer learning. This version uses [flite](http://www.festvox.org/flite/), which means the Inception model will tell you what it thinks it sees. Ideally, I want to make this even simpler and easier.

How to use it install flite:

```
sudo apt-get update

sudo apt-get install flite

```

Then to use the package:

```
import easy_inception

model = easy_inception.Inception()

model.classify(path_to_image)

model.close()
```

My original motivation to do this was to implement Inception in a way so that my son could use it to build a robot for his science fair project, based on [this](https://www.oreilly.com/learning/how-to-build-a-robot-that-sees-with-100-and-tensorflow), Lukas Biewald's project to build an object recognition robot.
