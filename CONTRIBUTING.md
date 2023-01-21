# Contributing


We're excited to collaborate with the community and look forward to the many improvements you can make to OpenTimelineIO!

## Project Roles and Responsibilities

If you are new to this project, and want to contribute, then please read
this document to understand the steps needed before you can submit code or changes to
the project.

Also see the [GOVERNANCE](GOVERNANCE.md) document for details on the rules and responsibilities of Contributors, Committers, and Technical Steering Committee members.

## Committers

The OpenTimelineIO Project Committers (alphabetically by last name) are:

- Daniel Flehner Heen ([apetrynet on github](https://github.com/apetrynet))
- Jeff Hodges ([jhodges10 on github](https://github.com/jhodges10))
- Darby Johnston ([darbyjohnston on github](https://github.com/darbyjohnston))
- Joshua Minor ([jminor on github](https://github.com/jminor))
- Jean-Christophe Morin ([JeanChristopheMorinPerso on github](https://github.com/JeanChristopheMorinPerso))
- Roger Nelson ([rogernelson on github](https://github.com/rogernelson))
- Nick Porcino ([meshula on github](https://github.com/meshula))
- Eric Reinecke ([reinecke on github](https://github.com/reinecke))
- Stephan Steinbach ([ssteinbach on github](https://github.com/ssteinbach))

## Contributor License Agreement

Before contributing code to OpenTimelineIO, we ask that you sign a Contributor License Agreement (CLA).
When you create a pull request, the Linux Foundation's EasyCLA system will guide you through the process of signing the CLA.

If you are unable to use the EasyCLA system, you can send a signed CLA to `opentimelineio-tsc@aswf.io` (please make sure to include your github username) and wait for confirmation that we've received it.

Here are the two possible CLAs:

* [OTIO_CLA_Corporate.pdf](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/raw/main/OTIO_CLA_Corporate.pdf): please sign this one for corporate use
* [OTIO_CLA_Individual.pdf](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/raw/main/OTIO_CLA_Individual.pdf): please sign this one if you're an individual contributor

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
git remote add upstream https://github.com/AcademySoftwareFoundation/OpenTimelineIO.git
```

Now you fetch the latest changes from the OpenTimelineIO repo like this:

```bash
git fetch upstream
git merge upstream/main
```

All the development should happen against the `main` branch.  We recommend you create a new branch for each feature or fix that you'd like to make and give it a descriptive name so that you can remember it later.  You can checkout a new branch and create it simultaneously like this:

```bash
git checkout -b mybugfix upstream/main
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

Now your remote branch will have your `mybugfix` branch, which you can now pull request (to OpenTimelineIO's `main` branch) using the github UI.

Please make sure that your pull requests are clean. In other words, address only the issue at hand. Split minor corrections, formatting clean ups, and the like into other PRs. Ensure that new work has coverage in a test. Ensure that any resultant behavioral changes in other parts of the library are called out. Use the rebase and squash git facilities as needed to ensure that the pull request does not contain non-informative remnants of old or superseded work.
