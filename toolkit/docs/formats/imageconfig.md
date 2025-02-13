# Image configuration

Image configuration consists of two sections - Disks and SystemConfigs - that describe the produced artifact(image). Image configuration code can be found in [configuration.go](../../tools/imagegen/configuration/configuration.go) and validity of the configuration file can be verified by the [imageconfigvalidator](../../tools/imageconfigvalidator/imageconfigvalidator.go)

## Disks

Disks entry specifies the disk configuration like its size (for virtual disks), partitions and partition table.

## TargetDisk

Required when building unattended ISO installer. This field defines the physical disk to which Azure Linux should be installed. The `Type` field must be set to `path` and the `Value` field must be set to the desired target disk path.

### Artifacts

Artifact (non-ISO image building only) defines the name, type and optional compression of the output Azure Linux image.

Sample Artifacts entry, creating a raw rootfs, compressed to .tar.gz format(note that this format does not support partitions, so there would be no "Partitions" entry):

``` json
"Artifacts": [
    {
        "Name": "core",
        "Compression": "tar.gz"
    }
]

```

Sample Artifacts entry, creating a vhdx disk image:

``` json
"Artifacts": [
    {
        "Name": "otherName",
        "Type": "vhdx"
    }
],
```

### Partitions

"Partitions" key holds an array of Partition entries.

Partition defines the size, name and file system type for a partition.
"Start" and "End" fields define the offset from the beginning of the disk in MBs.
An "End" value of 0 will determine the size of the partition using the next
partition's start offset or the value defined by "MaxSize", if this is the last
partition on the disk.

Note that Partitions do not have to be provided; the resulting image is going to be a rootfs.

Supported partition FsTypes: fat32, fat16, vfat, ext2, ext3, ext4, xfs, linux-swap.

Sample partitions entry, specifying a boot partition and a root partition:

``` json
"Partitions": [
    {
        "ID": "boot",
        "Flags": [
            "esp",
            "boot"
        ],
        "Start": 1,
        "End": 9,
        "FsType": "fat32"
    },
    {
        "ID": "rootfs",
        "Start": 9,
        "End": 0,
        "FsType": "ext4",
        "Type": "linux-root-amd64"
    }
]
```

#### Flags

"Flags" key controls special handling for certain partitions.

- `esp` indicates this is the UEFI esp partition
- `grub` indicates this is a grub boot partition
- `bios_grub` indicates this is a bios grub boot partition
- `boot` indicates this is a boot partition
- `dmroot` indicates this partition will be used for a device mapper root device (i.e. `Encryption`)

#### TypeUUID

"TypeUUID" key sets the partition type UUID. The "Type" key can be used instead to set the partition type using a friendly name.

- `linux`: "0fc63daf-8483-4772-8e79-3d69d8477de4",
- `esp`: "c12a7328-f81f-11d2-ba4b-00a0c93ec93b",
- `xbootldr`: "bc13c2ff-59e6-4262-a352-b275fd6f7172",
- `linux-root-amd64`: "4f68bce3-e8cd-4db1-96e7-fbcaf984b709",
- `linux-swap`: "0657fd6d-a4ab-43c4-84e5-0933c84b4f4f",
- `linux-home`: "933ac7e1-2eb4-4f13-b844-0e14e2aef915",
- `linux-srv`: "3b8f8425-20e0-4f3b-907f-1a25a76f98e8",
- `linux-var`: "4d21b016-b534-45c2-a9fb-5c16e091fd2d",
- `linux-tmp`: "7ec6f557-3bc5-4aca-b293-16ef5df639d1",
- `linux-lvm`: "e6d6d379-f507-44c2-a23c-238f2a3df928",
- `linux-raid`: "a19d880f-05fc-4d3b-a006-743f0f84911e",
- `linux-luks`: "ca7d7ccb-63ed-4c53-861c-1742536059cc",
- `linux-dm-crypt`: "7ffec5c9-2d00-49b7-8941-3ea10a5586b7",

## SystemConfigs

SystemConfigs is an array of SystemConfig entries.

SystemConfig defines how each system present on the image is supposed to be configured.

### IsKickStartBoot

IsKickStartBoot is a boolean that determines whether this is a kickstart-style installation. It will determine whether to perform kickstart-specific operations like executing preinstall scripts and parsing kickstart partitioning file.

### PartitionSettings

PartitionSettings key is an array of PartitionSetting entries.

PartitionSetting holds the mounting information for each partition.

A sample PartitionSettings entry, designating an EFI and a root partitions:

``` json
"PartitionSettings": [
    {
        "ID": "boot",
        "MountPoint": "/boot/efi",
        "MountOptions" : "umask=0077"
    },
    {
        "ID": "rootfs",
        "MountPoint": "/"
    }
],
```

A PartitionSetting may set a `MountIdentifier` to control how a partition is identified in the `fstab` file. The supported options are `uuid`, `partuuid`, and `partlabel`. If the `MountIdentifier` is omitted `partuuid` will be selected by default.

`partlabel` may not be used with `mbr` disks, and requires the `Name` key in the corresponding `Partition` be populated. An example with the rootfs mounted via `PARTLABEL=my_rootfs`, but the boot mount using the default `PARTUUID=<PARTUUID>`:

``` json
"Partitions": [

    ...

    {
        "ID": "rootfs",
        "Name": "my_rootfs",
        "Start": 9,
        "End": 0,
        "FsType": "ext4"
    }
]
```

``` json
"PartitionSettings": [
    {
        "ID": "boot",
        "MountPoint": "/boot/efi",
        "MountOptions" : "umask=0077"
    },
    {
        "ID": "rootfs",
        "MountPoint": "/",
        "MountIdentifier": "partlabel"
    }
],
```

It is possible to use `PartitionSettings` to configure diff disk image creation. Two types of diffs are possible.
`rdiff` and `overlay` diff.

For small and deterministic images `rdiff` is a better algorithm.
For large images based on `ext4` `overlay` diff is a better algorithm.

A sample `ParitionSettings` entry using `rdiff` algorithm:

``` json
{
    "ID": "boot",
    "MountPoint": "/boot/efi",
    "MountOptions" : "umask=0077",
    "RdiffBaseImage" : "../out/images/core-efi/core-efi-1.0.20200918.1751.ext4"
},
 ```

A sample `ParitionSettings` entry using `overlay` algorithm:

``` json
{
   "ID": "rootfs",
   "MountPoint": "/",
   "OverlayBaseImage" : "../out/images/core-efi/core-efi-rootfs-1.0.20200918.1751.ext4"
}

```

`RdiffBaseImage` represents the base image when `rdiff` algorithm is used.
`OverlayBaseImage` represents the base image when `overlay` algorithm is used.

### EnableGrubMkconfig

EnableGrubMkconfig is a optional boolean that controls whether the image uses grub2-mkconfig to generate the boot configuration (/boot/grub2/grub.cfg) or not. If EnableGrubMkconfig is specified, only valid values are `true` and `false`. Default is `true`.

### EnableSystemdFirstboot

EnableSystemdFirstboot is a optional boolean that controls whether the image will run the systemd-firstboot service on first boot. Setting to `true` will set `/etc/machine-id` to `"uninitialized"`, while setting to `false` will leave `/etc/machine-id` blank. See [https://www.freedesktop.org/software/systemd/man/latest/machine-id.html] for more information. By default firstboot is disabled.

### PackageLists

PackageLists key consists of an array of relative paths to the package lists (JSON files).

All of the files listed in PackageLists are going to be scanned in a linear order to obtain a final list of packages for the resulting image by taking a union of all packages. **It is recommended that initramfs is the last package to speed up the installation process.**

PackageLists **must not include kernel packages**! To provide a kernel, use KernelOptions instead. Providing a kernel package in any of the PackageLists files results in an **undefined behavior**.

If any of the packages depends on a kernel, make sure that the required kernel is provided with KernelOptions.

A sample PackageLists entry pointing to three files containing package lists:

``` json
"PackageLists": [
    "packagelists/hyperv-packages.json",
    "packagelists/core-packages-image.json",
    "packagelists/cloud-init-packages.json"
],
```

### Disabling Documentation and Locales

For size constrained images it may be desirable to omit documentation and non-default locales from an image.

``` json
"DisableRpmDocs": true,
"OverrideRpmLocales": "NONE",
```

`DisableRpmDocs` will configure the image to never install the documentation. Selecting `OverrideRpmLocales=NONE` will omit all locales from the image.

These customizations are encoded into `/usr/lib/rpm/macros.d/macros.installercustomizations_*` files on the final system. They set values for `%_excludedocs` and `%_install_langs` respectively.

#### Custom Locales

A specific locale string may also be set using:

``` json
"OverrideRpmLocales": "en:fr:es"
```

This may be any value compatible with the `%_install_langs` rpm macro.

#### Restoring Documentation and Locales on an Installed System

The `OverrideRpmLocales` and `DisableRpmDocs` settings are stored in `/usr/lib/rpm/macros.d/macros.installercustomizations_*` files on the final system. The files selected for install are based on the `rpm` macros at the time of transaction, so to restore these files on an installed system remove the associated macro definition and run  `tdnf -y reinstall $(rpm -qa)`. This will reinstall all packages and apply the new settings.

### Customization Scripts

The tools offer the option of executing arbitrary shell scripts during various points of the image generation process. There are three points that scripts can be executed: `PreInstall`, `PostInstall`, and `ImageFinalize`.

>Installer starts -> `PreInstallScripts` -> Create Partitions -> Install Packages -> `PostInstallScripts` -> Configure Bootloader (if any) -> `ImageFinalizeScripts`

Each of the `PreInstallScripts`, `PostInstallScripts`, and `FinalizeImageScripts` entires are an array of file paths and the corresponding input arguments. The scripts will be executed in sequential order and within the context of the final image. The file paths are relative to the image configuration file. Scripts may be passed without arguments if desired.

All scripts follow the same format in the image config .json file:

``` json
"PreInstallScripts | PostInstallScripts | FinalizeImageScripts":[
    {
        "Path": "arglessScript.sh"
    },
    {
        "Path": "ScriptWithArguments.sh",
        "Args": "--input abc --output cba"
    }
],
```

#### PreInstallScripts

There are customer requests that would like to use a Kickstart file to install Azure Linux OS. Kickstart installation normally includes pre-install scripts that run before installation begins and are normally used to handle tasks like network configuration, determining partition schema etc. The `PreInstallScripts` field allows for running customs scripts for similar purposes. Sample Kickstart pre-install script [here](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/5/html/installation_guide/s1-kickstart2-preinstallconfig). You must set the `IsKickStartBoot` to true in order to make the installer execute the preinstall scripts.

The preinstall scripts are run from the context of the installer, NOT the installed system (since it doesn't exist yet).

**NOTE**: currently, Azure Linux's pre-install scripts are mostly intended to provide support for partitioning schema configuration. For this purpose, make sure the script creates a proper configuration file (example [here](https://www.golinuxhub.com/2018/05/sample-kickstart-partition-example-raid/)) under `/tmp/part-include` in order for it to be consumed by Azure Linux's image building tools.

#### PostInstallScripts

PostInstallScripts run immediately after all packages have been installed, but before image finalization steps are taken (configure bootloader, record read-only disks, etc). The postinstall scripts are run from the context of the installed system.

#### FinalizeImageScripts

FinalizeImageScripts provide the opportunity to run shell scripts to customize the image before it is finalized (converted to .vhdx, etc.). The finalizeimage scripts are run from the context of the installed system.

### AdditionalFiles

The `AdditionalFiles` list provides a mechanism to add arbitrary files to the image. The elements are are `"src": "dst"` pairs.

`src` is relative to the image config `.json` file.

The `dst` can be one of:

- A string representing the destination absolute path, OR
- An object (`FileConfig`) containing the destination absolute path and other file options, OR
- An array containing a mixture of strings and objects, which allows a single source file to be copied to multiple destination paths.

ISO installers will include the files on the installation media and will place them into the final installed image.

```json
    "AdditionalFiles": [
        "../../out/tools/imager": "/installer/imager",
        "additionalconfigs": [
            "/etc/my/config.conf",
            {
                "Path": "/etc/yours/config.conf",
                "Permissions": "664"
            }
        ]
    ]
```

#### FileConfig

`FileConfig` provides options to modify metadata of files copied using `AdditionalFiles`.

Fields:

- `Path`: The destination absolute path.
- `Permissions`: The file permissions to apply to the file.

  Supported value formats:

  - Octal string: A JSON string containing an octal number. e.g. `"664"`

### Networks

The `Networks` entry is added to enable the users to specify the network configuration parameters to enable users to set IP address, configure the hostname, DNS etc. Currently, the Azure Linux tooling only supports a subset of the kickstart network command options: `bootproto`, `gateway`, `ip`, `net mask`, `DNS` and `device`. Hostname can be configured using the `Hostname` entry of the image config.

A sample Networks entry pointing to one network configuration:

``` json
    "Networks":[
    {
        "BootProto": "dhcp",
        "GateWay":   "192.168.20.4",
        "Ip":        "192.169.20.148",
        "NetMask":   "255.255.255.0",
        "OnBoot":    false,
        "NameServers": [
            "192.168.30.23"
        ],
        "Device": "eth0"
    }
],
```

### PackageRepos

The `PackageRepos` list defines custom package repos to use with **ISO installers**. Each repo must set `Name` and `BaseUrl`. Each repo may also set `GPGCheck`/`RepoGPGCheck` (both default to `true`), `GPGKeys` (a string of the form `file:///path/to/key1 file:///path/to/key2 ...`. `GPGKeys` defaults to the Microsoft RPM signing keys if left unset), and `Install` which causes the repo file to be installed into the final image.

If a custom repo entry is present, the default local file repo entires **will not be used during install**. If you want to also use them you will need to add an entry for [local.repo](toolkit/resources/manifests/image/local.repo) into the repo list. The default behavior is to pre-download the required packages into the ISO installer from repos defined in `REPO_LIST`.

By default the repo will only be used during ISO install, it may also be made available to the installed image by setting `Install` to `true`.

> **Currently ISO installers don't support custom keys. Only installed repos support them. The keys must be provisioned via [AdditionalFiles](#additionalfiles)**

```json
"PackageRepos": [
    {
        "Name":     "PackageMicrosoftComMirror",
        "BaseUrl":  "https://contoso.com/pmc-mirror/$releasever/prod/base/$basearch",
        "Install":  false,
    },
    {
        "Name":     "MyCopyOfOfficialRepo",
        "BaseUrl":  "https://contoso.com/cbl-mariner-custom-packages/$releasever/prod/base/$basearch",
        "Install":  true,
        "GPGCheck": true,
        "RepoGPGCheck": false,
        "GPGKeys": "file:///etc/pki/rpm-gpg/my-custom-key"
    }
]
```

### RemoveRpmDb

RemoveRpmDb triggers RPM database removal after the packages have been installed.
Removing the RPM database may break any package managers inside the image.

### PreserveTdnfCache

PreserveTdnfCache leaves the `tdnf` cache intact after image generation. By default the cache will be cleaned via `tdnf clean all` to save space after installing packages and running `PostInstallScripts`.

### KernelOptions

KernelOptions key consists of a map of key-value pairs, where a key is an identifier and a value is a name of the package (kernel) used in a scenario described by the identifier. During the build time, all kernels provided in KernelOptions will be built.

KernelOptions is mandatory for all non-`rootfs` image types.

KernelOptions may be included in `rootfs` images which expect a kernel, such as the initrd for an ISO, if desired.

Currently there is only one key with an assigned meaning:

- `default` key needs to be always provided. It designates a kernel that is used when no other scenario is applicable (i.e. by default).

Keys starting with an underscore are ignored - they can be used for providing comments.

A sample KernelOptions specifying a default kernel:

``` json
"KernelOptions": {
    "default": "kernel"
},
```

### ReadOnlyVerityRoot

ReadOnlyVerityRoot has been deprecated in the image configuration. The feature is suppored in the [Azure Linux Image Customizer](../../tools/imagecustomizer/README.md) tool now.

See [Azure Linux Image Customizer configuration](../../tools/imagecustomizer/docs/configuration.md#verity-type) for more information.

### KernelCommandLine

KernelCommandLine is an optional key which allows additional parameters to be passed to the kernel when it is launched from Grub.

#### ImaPolicy

ImaPolicy is a list of Integrity Measurement Architecture (IMA) policies to enable, they may be any combination of `tcb`, `appraise_tcb`, `secure_boot`.

#### EnableFIPS

EnableFIPS is a optional boolean option that controls whether the image tools create the image with FIPS mode enabled or not. If EnableFIPS is specificed, only valid values are `true` and `false`.

#### ExtraCommandLine

ExtraCommandLine is a string which will be appended to the end of the kernel command line and may contain any additional parameters desired. The `` ` `` character is reserved and may not be used. **Note: Some kernel command line parameters are already configured by default in [grub.cfg](../../tools/internal/resources/assets/grub2/grub.cfg) and [/etc/default/grub](../../tools/internal/resources/assets/grub2/grub) for mkconfig-based images. Many command line options may be overwritten by passing a new value. If a specific argument must be removed from the existing grub template a `FinalizeImageScript` is currently required.

#### SELinux

The Security Enhanced Linux (SELinux) feature is enabled by using the `SELinux` key, with value containing the mode to use on boot.  The `enforcing` and `permissive` values will set the mode in /etc/selinux/config.
This will instruct init (systemd) to set the configured mode on boot.  The `force_enforcing` option will set enforcing in the config and also add `enforcing=1` in the kernel command line,
which is a higher precedent than the config file. This ensures SELinux boots in enforcing even if the /etc/selinux/config was altered.

#### SELinuxPolicy

An optional field to overwrite the SELinux policy package name. If not set, the default is `selinux-policy`.

#### CGroup

The version for CGroup in Azure Linux images can be enabled by using the `CGroup` key with value containing which version to use on boot. The value that can be chosen is either `version_one` or `version_two`.
The `version_two` value will set the cgroupv2 to be used in Azure Linux by setting the config value `systemd.unified_cgroup_hierarchy=1` in the default kernel command line. The value `version_one` or no value set will keep cgroupv1 (current default) to be enabled on boot.
For more information about cgroups with Kubernetes, see [About cgroupv2](https://kubernetes.io/docs/concepts/architecture/cgroups/).

A sample KernelCommandLine enabling a basic IMA mode and passing two additional parameters:

``` json
"KernelCommandLine": {
    "ImaPolicy": ["tcb"],
    "ExtraCommandLine": "my_first_param=foo my_second_param=\"bar baz\""
},
```

A sample KernelCommandLine enabling SELinux and booting in enforcing mode:

``` json
"KernelCommandLine": {
    "SELinux": "enforcing"
},
```

A sample KernelCommandLine enabling SELinux and overwriting the default 'selinux-policy' package name:

``` json
"KernelCommandLine": {
    "SELinux": "enforcing",
    "SELinuxPolicy": "my-selinux-policy"
},
```

A sample KernelCommandLine enabling CGroup and booting with cgroupv2 enabled:

``` json
"KernelCommandLine": {
    "CGroup": "version_two"
},
```

### EnableHidepid

An optional flag that enables the stricter `hidepid` option in `/proc` (`hidepid=2`). `hidepid` prevents proc IDs from being visible to all users.

### Users

Users is an array of user information. The User information is a map of key value pairs.

The image generated has users matching the values specified in Users.

The table below are the keys for the users.

|Key                |Type               |Restrictions
--------------------|:------------------|:------------------------------------------------
|Name               |string             |Cannot be empty
|UID                |string             |Must be in range 0-60000
|PasswordHashed     |bool               |
|Password           |string             |If 'PasswordHashed=true', use `openssl passwd ...` to generate the password hash
|PasswordExpiresDays|number             |Must be in range 0-99999 or -1 for no expiration
|SSHPubKeyPaths     |array of strings   |
|PrimaryGroup       |string             |
|SecondaryGroups    |array of strings   |
|StartupCommand     |string             |
|HomeDirectory      |string             |

An example usage for users "root" and "basicUser" would look like:

``` json
"Users": [
    {
        "Name": "root",
        "PasswordHashed": true,
        "Password": "$6$<SALT>$<HASHED PASSWORD>",
        "_comment": "Generated with `openssl passwd -6 -salt <SALT> <PASSWORD>`",
    },
    {
        "Name": "basicUser",
        "Password": "someOtherPassword",
        "UID": 1001
    }
]
```

# Sample image configuration

A sample image configuration, producing a VHDX disk image:

``` json
{
    "Disks": [
        {
            "PartitionTableType": "gpt",
            "MaxSize": 11264,
            "Artifacts": [
                {
                    "Name": "core",
                    "Type": "vhdx"
                }
            ],
            "Partitions": [
                {
                    "ID": "boot",
                    "Flags": [
                        "esp",
                        "boot"
                    ],
                    "Start": 1,
                    "End": 9,
                    "FsType": "fat32"
                },
                {
                    "ID": "rootfs",
                    "Start": 9,
                    "End": 0,
                    "FsType": "ext4",
                    "Type": "linux-root-amd64"
                }
            ]
        }
    ],
    "SystemConfigs": [
        {
            "Name": "Standard",
            "BootType": "efi",
            "PartitionSettings": [
                {
                    "ID": "boot",
                    "MountPoint": "/boot/efi",
                    "MountOptions" : "umask=0077",
                    "RdiffBaseImage" : "../out/images/core-efi/core-efi-1.0.20200918.1751.ext4"
                },
                {
                    "ID": "rootfs",
                    "MountPoint": "/",
                     "OverlayBaseImage" : "../out/images/core-efi/core-efi-rootfs-1.0.20200918.1751.ext4"
                }
            ],
            "PackageLists": [
                "packagelists/hyperv-packages.json",
                "packagelists/core-packages-image.json",
                "packagelists/cloud-init-packages.json"
            ],
            "KernelOptions": {
                "default": "kernel"
            },
            "KernelCommandLine": {
                "ImaPolicy": ["tcb"],
                "ExtraCommandLine": "my_first_param=foo my_second_param=\"bar baz\""
            },
            "Hostname": "azurelinux"
        }
    ]
}

```
