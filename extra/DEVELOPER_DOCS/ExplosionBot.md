# Explosion-bot

Explosion-bot is a robot that can be invoked to help with running particular test commands.

## Permissions

Only maintainers have permissions to summon explosion-bot. Each of the open source repos that use explosion-bot has its own team(s) of maintainers, and only github users who are members of those teams can successfully run bot commands.

## Running robot commands

To summon the robot, write a github comment on the issue/PR you wish to test. The comment must be in the following format:

```
@explosion-bot please test_gpu
```

Some things to note:

* The `@explosion-bot please` must be the beginning of the command - you cannot add anything in front of this or else the robot won't know how to parse it. Adding anything at the end aside from the test name will also confuse the robot, so keep it simple!
* The command name (such as `test_gpu`) must be one of the tests that the bot knows how to run. The available commands are documented in the bot's [workflow config](https://github.com/explosion/spaCy/blob/master/.github/workflows/explosionbot.yml#L26) and must match exactly one of the commands listed there.
* The robot can't do multiple things at once, so if you want it to run multiple tests, you'll have to summon it with one comment per test.
* For the `test_gpu` command, you can specify an optional thinc branch (from the spaCy repo) or a spaCy branch (from the thinc repo) with either the `--thinc-branch` or `--spacy-branch` flags. By default, the bot will pull in the PR branch from the repo where the command was issued, and the main branch of the other repository. However, if you need to run against another branch, you can say (for example):

```
@explosion-bot please test_gpu --thinc-branch develop
```
You can also specify a branch from an unmerged PR:
```
@explosion-bot please test_gpu --thinc-branch refs/pull/633/head
```

## Troubleshooting

If the robot isn't responding to commands as expected, you can check its logs in the [Github Action](https://github.com/explosion/spaCy/actions/workflows/explosionbot.yml). 

For each command sent to the bot, there should be a run of the `explosion-bot` workflow. In the `Install and run explosion-bot` step, towards the ends of the logs you should see info about the configuration that the bot was run with, as well as any errors that the bot encountered.
