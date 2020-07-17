# Contributing


We're excited to collaborate with the community and look forward to the many improvements you can make to OpenTimelineIO!

## Contributor License Agreement

Before contributing code to OpenTimelineIO, we ask that you sign a Contributor License Agreement (CLA).  At the root of the repo you can find the two possible CLAs:

* [OTIO_CLA_Corporate.pdf](https://github.com/PixarAnimationStudios/OpenTimelineIO/raw/master/OTIO_CLA_Corporate.pdf): please sign this one for corporate use
* [OTIO_CLA_Individual.pdf](https://github.com/PixarAnimationStudios/OpenTimelineIO/raw/master/OTIO_CLA_Individual.pdf): please sign this one if you're an individual contributor

Once your CLA is signed, send it to `opentimelineio-cla@pixar.com` (please make sure to include your github username) and wait for confirmation that we've received it.  After that, you can submit pull requests.

## Coding Conventions
Please follow the coding convention and style in each file and in each library when adding new files.

## Git Workflow
Here is the workflow we recommend for working on OpenTimelineIO if you intend on contributing changes back:

Post an issue on github to let folks know about the feature or bug that you found, and mention that you intend to work on it.  That way, if someone else is working on a similar project, you can collaborate, or you can get early feedback which can sometimes save time.

Use the github website to fork your own private repository.

Clone your fork to your local machine, like this:

```bash
git clone https://github.com/you/OpenTimelineIO.git
```

Add the primary OpenTimelineIO repo as upstream to make it easier to update your remote and local repos with the latest changes:

```bash
cd OpenTimelineIO
git remote add upstream https://github.com/PixarAnimationStudios/OpenTimelineIO.git
```

Now you fetch the latest changes from Pixar's OpenTimelineIO repo like this:

```bash
git fetch upstream
```

All the development should happen against the `master` branch.  We recommend you create a new branch for each feature or fix that you'd like to make and give it a descriptive name so that you can remember it later.  You can checkout a new branch and create it simultaneously like this:

```bash
git checkout -b mybugfix upstream/master
```

Now you can work in your branch locally.

Once you are happy with your change, you can verify that the change didn't cause tests failures by running tests like this:

```bash
make test
make lint
```

If all the tests pass and you'd like to send your change in for consideration, push it to your remote repo:

```bash
git push origin mybugfix
```

Now your remote branch will have your `mybugfix` branch, which you can now pull request (to OpenTimelineIO's `master` branch) using the github UI.

Please make sure that your pull requests are clean.  Use the rebase and squash git facilities as needed to ensure that the pull request is as clean as possible.
