# policy
Collection of security policies

Directories:
    * osv -- dover versions of the OSV policies
    * dover-private -- dover proprietary policies

Entity Files

The policy linker and build system uses a number of entity description
files to determine how to apply metadata to the runtime binary image
and at startup.

The policy test scripts copy the relevant files into the correct
locations, based upon file naming conventions. All origional source
entity files are located in the entities dir in this repo. If not
matching entity file is found in entities dir then and empty file is
created.

Kernel Entities

The install-kernels target will look for an entity file for the policy
being installed and copy that file to the policy install dir. Later
the test script will copy the entity file from the policy install dir
to the test dir. Policy entity files use the naming convention:

   * qualified.policy.name.entities.yml

Test File Entities

Each test source file can also define an entity file for that
application, if not defined an empty file will be created. These files
are also found in the entities dir and have a similar naming
convention:

   * file_name.c.entities.yml

