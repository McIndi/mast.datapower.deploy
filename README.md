# mast.datapower.deploy
A revised deployment process automation

# Introduction

The new MAST for IBM DataPower deployment tool is slightly opionionated, but
it is meant to provide the following benefits:

1. Repeatable deployments following best practices
2. Services can move freely between environments after passing all tests
3. Dependable framework for processes surrounding service development which
will help your developerment, administration and operations teams.
4. Full audit trail of all changes

By following the procedures in this document and by using this tool, your
organization can benefit in many ways.

# Overview

## Integration

This tool integrates with the following version control systems (VCS):

1. git
2. svn (Requires an SVN client command line tool to be available on
your system's PATH)
3. TFS (Requires TEE.exe (Team Explorer Everywhere) to be available
on your system's PATH)

## Directory Structure

### Basics

This tool expects the repository to follow a certain directory structure.

In the root directory, there should be a directory called `config` which holds
any service zips or xml files which will be `import`ed into the proper domain.

As a peer to the `config` directory there should be a directory called `local`
any files in this directory will be deployed to the DataPower into `local:///`
respecting directory structure. For instance, if the following directory
structure exists in the project's root directory:

```
.
├── config
│   ├── service_1.zip
│   └── service_2.xml
└── local
    ├── service_1
    │   ├── config.xml
    │   └── service.xslt
    └── service_2
        ├── config.xml
        └── service.xslt
```

Then on each deployment would import service_1.zip and service_2.xml. After
that, the files `./local/service_1/config.xml` and
`./local/service_1/service.xslt` would end up in the `local:///service_1/`
directory in the proper domain. Also, the files `./local/service_2/config.xml`
and `./local/service_2/service.xslt` would be deployed to the
`local:///service_2/` directory in the proper domain.

### Environment Specific Files

This tool also has the ability to handle any custom configuration needed in
your various environments. Before using this functionality, you need to review
the [configuration guide](#configuration-guide). After properly configuring
your deployment environments, you can have a directory with the same name
as one of your environments. Inside this directory, you can have a couple of
different subdirectories.

You can have a directory called `deploymentPolicy`, which should have an
export of a deployment policy. The export will be imported into the proper
domain and applied to all imports done during the deployment.

You can aslo have a directory called `local` and this will be treated the same
as the `local` directory outlined above except they will only be uploaded when
deploying to this environment.














