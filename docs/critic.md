# OperaCritic Code Review for GitHub-hosted Repositories: A User's Guide #

## Introduction ##

Critic is a code review system designed to work with git to provide a
smooth review workflow sutiable for a wide range of projects including
those with a large number of contributers, non-trivial code ownership
rules and large, complex, patches.

## Comparison to GitHub Code Review ##

For projects hosted on GitHub, the obvious choice for code review is
the built-in pull request comment functionality. Compared to this,
critic offers a number of advantages:

* Changes are automatically assigned to only the people able to review
  them, using a system of filters. Different parts of a review may
  have different owners.

* Reviews can be spread over time and over multiple reviewers using
  per-file status markers to track which parts have already been reviewed.

* Diffs are presented in a side-by-side view so that reviewers may
  read the changed code in context. In addition the diff view is
  expandable in-place allowing an arbitary amount of context to be shown.

* Clear tracking of the work required to merge the change. Issues
  raised on the review are automatically marked as fixed when
  subsequent commits change the lines they applied to. Issues may be
  reopened or manually resolved by the reviewer. A review is
  automatically accepted when there are 0 outstanding issues.

* Better notifications. Because reviewers only get notified for review
  requests that they can actually review, and because there is an
  explicit "submit" step for changes made to reviews, critic tends to
  produce a smaller number of higher-value emails than GitHub.

There are also a number of disadvantages of critic compared to GitHub
code review tools:

* The UI is not so polished and may take some getting used to.

* As an external tool, there are more moving parts than using GitHub
  alone, so it is possible fot things to go wrong.

## Critic for Patch Authors ##

### Submitting a Review Request ###

Where Critic is used in conjunction with GitHub, the process for
submitting a patch is identical to the ordinary GitHub
workflow. When you create a pull request, a corresponding Critic
review will automatically be created. Pushes to the pull request will
automatically be reflected in the review and merging or closing the
pull request will automatically close the corresponding review.

Once your pull request has been created, the Critic software will
automatically add a comment to the pull request page linking to the
corresponding critic review.

Add email address

Review UI

Dealing with comments

## Critic for Reviewers ##

Adding filters

The dashboard

Getting started with a review

Raising issues

Marking files as reviewed

