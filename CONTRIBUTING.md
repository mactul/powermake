# Contributing

- [Contributing](#contributing)
  - [Feature request](#feature-request)
    - [Something is completely impossible to do with PowerMake.](#something-is-completely-impossible-to-do-with-powermake)
    - [Something useful is missing in powermake](#something-useful-is-missing-in-powermake)
  - [Bug found](#bug-found)
  - [I want to contribute to the codebase](#i-want-to-contribute-to-the-codebase)

You want to contribute ? That's great !

Here is some guidelines to make sure your contribution will be helpful.

## Feature request

### Something is completely impossible to do with PowerMake.

The main idea of PowerMake is that everything should be possible to do, you may just have to write missing features by yourself in your makefile.  
If you find something that is impossible to do by the PowerMake design, that's a priority.  
In this situation, please [open an issue](https://github.com/mactul/powermake/issues/new) with **both** the tags **bug** and **feature request**.

### Something useful is missing in powermake

A lot of things are missing in powermake, but we are interested to know what are the things that miss you the most.  
You can [open an issue](https://github.com/mactul/powermake/issues/new) with the tag **feature request** and hopefully we will add your request in one of the upcoming releases.


## Bug found

Something isn't working as expected with powermake ?  
Please, [open an issue](https://github.com/mactul/powermake/issues/new) with the tag **bug**.


## I want to contribute to the codebase

If you have the time, skill and motivation to help us improve powermake, you are welcome !

You can start by sending a pull request and if your code is good enough, it will be merged into the project.

To make sure your pull request will not be rejected, here are the crucial guideline we want you to follow:

- Undocumented feature will always be rejected.
  - Every new feature should be documented at user end (in the README.md) to be published.
  - Internal documentation of your code is not a big deal as long as your code is readable and has good namings.
- commit to `dev` or a branch created for your feature, not to `main`.
  - small changes can be directly commited to `dev` and will the be merged to `main` after.
  - big features should create their own branch to facilitate the merging work.
- Avoid sending huge pull requests affecting all files
  - Because every pull request should be entirely reviewed and merged with other commits, huge pull request are extremely inconvenient.
  - Try to cut your commits to one feature by pull request.
- Use 4 spaces for indentation.
  - The whole project use spaces for indentation and python doesn't like the mix at all.
- Your code should approximately follow the pep8 syntax.
  - It's not a problem if your code doesn't respect the pep8 syntax at 100%, but your code should be readable, with spaces around operators, etc...