// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package imagecustomizerapi

import (
	"fmt"
)

type Storage struct {
	ResetPartitionsUuidsType ResetPartitionsUuidsType `yaml:"resetPartitionsUuidsType"`
	BootType                 BootType                 `yaml:"bootType"`
	Disks                    []Disk                   `yaml:"disks"`
	FileSystems              []FileSystem             `yaml:"filesystems"`
	Verity                   []Verity                 `yaml:"verity"`
}

func (s *Storage) IsValid() error {
	var err error

	err = s.ResetPartitionsUuidsType.IsValid()
	if err != nil {
		return err
	}

	err = s.BootType.IsValid()
	if err != nil {
		return err
	}

	if len(s.Disks) > 1 {
		return fmt.Errorf("defining multiple disks is not currently supported")
	}

	for i := range s.Disks {
		disk := &s.Disks[i]

		err := disk.IsValid()
		if err != nil {
			return fmt.Errorf("invalid disk at index %d:\n%w", i, err)
		}
	}

	fileSystemSet := make(map[string]FileSystem)
	for i, fileSystem := range s.FileSystems {
		err = fileSystem.IsValid()
		if err != nil {
			return fmt.Errorf("invalid filesystems item at index %d:\n%w", i, err)
		}

		if _, existingName := fileSystemSet[fileSystem.DeviceId]; existingName {
			return fmt.Errorf("duplicate fileSystem deviceId used (%s) at index %d", fileSystem.DeviceId, i)
		}

		fileSystemSet[fileSystem.DeviceId] = fileSystem
	}

	if len(s.Verity) > 1 {
		return fmt.Errorf("defining multiple verity devices is not currently supported")
	}

	for i, verity := range s.Verity {
		err = verity.IsValid()
		if err != nil {
			return fmt.Errorf("invalid verity item at index %d:\n%w", i, err)
		}
	}

	hasResetUuids := s.ResetPartitionsUuidsType != ResetPartitionsUuidsTypeDefault
	hasBootType := s.BootType != BootTypeNone
	hasDisks := len(s.Disks) > 0
	hasFileSystems := len(s.FileSystems) > 0
	hasVerity := len(s.Verity) > 0

	if hasResetUuids && hasDisks {
		return fmt.Errorf("cannot specify both 'resetPartitionsUuidsType' and 'disks'")
	}

	if !hasBootType && hasDisks {
		return fmt.Errorf("must specify 'bootType' if 'disks' are specified")
	}

	if hasBootType && !hasDisks {
		return fmt.Errorf("cannot specify 'bootType' without specifying 'disks'")
	}

	if hasFileSystems && !hasDisks {
		return fmt.Errorf("cannot specify 'filesystems' without specifying 'disks'")
	}

	if hasVerity && !hasDisks {
		return fmt.Errorf("cannot specify 'verity' without specifying 'disks'")
	}

	partitionSet := make(map[string]Partition)
	espPartitionExists := false
	biosBootPartitionExists := false
	partitionLabelCounts := make(map[string]int)

	for i, disk := range s.Disks {
		for j, partition := range disk.Partitions {
			if _, existingName := partitionSet[partition.Id]; existingName {
				return fmt.Errorf("invalid disk at index %d:\nduplicate partition id used (%s) at index %d", i,
					partition.Id, j)
			}

			partitionSet[partition.Id] = partition

			fileSystem, hasFileSystem := fileSystemSet[partition.Id]

			// Ensure special partitions have the correct filesystem type.
			switch partition.Type {
			case PartitionTypeESP:
				espPartitionExists = true

				if !hasFileSystem || (fileSystem.Type != FileSystemTypeFat32 && fileSystem.Type != FileSystemTypeVfat) {
					return fmt.Errorf("ESP partition (%s) must have 'fat32' or 'vfat' filesystem type", partition.Id)
				}

			case PartitionTypeBiosGrub:
				biosBootPartitionExists = true

				if hasFileSystem {
					if fileSystem.Type != "" {
						return fmt.Errorf("BIOS boot partition (%s) must not have a filesystem 'type'",
							partition.Id)
					}

					if fileSystem.MountPoint != nil {
						return fmt.Errorf("BIOS boot partition (%s) must not have a 'mountPoint'", partition.Id)
					}
				}
			}

			// Ensure filesystem entires with a mountPoint also have a filesystem type value.
			if hasFileSystem && fileSystem.MountPoint != nil && fileSystem.Type == FileSystemTypeNone {
				return fmt.Errorf("filesystem with 'mountPoint' must have a 'type'")
			}

			// Count the number of partitions that use each label.
			partitionLabelCounts[partition.Label] += 1
		}
	}

	veritySet := make(map[string]Verity)
	for i, verity := range s.Verity {
		if _, existingName := partitionSet[verity.Id]; existingName {
			return fmt.Errorf("invalid verity item at index %d:\nid (%s) conflicts with partition id", i, verity.Id)
		}

		if _, existingName := veritySet[verity.Id]; existingName {
			return fmt.Errorf("invalid verity item at index %d:\nduplicate id used (%s)", i, verity.Id)
		}

		veritySet[verity.Id] = verity

		_, foundDataPartition := partitionSet[verity.DataDeviceId]
		if !foundDataPartition {
			return fmt.Errorf("invalid verity at index %d:\nno partition with matching ID (%s)", i,
				verity.DataDeviceId)
		}

		_, foundHashPartition := partitionSet[verity.HashDeviceId]
		if !foundHashPartition {
			return fmt.Errorf("invalid verity at index %d:\nno partition with matching ID (%s)", i,
				verity.HashDeviceId)
		}
	}

	// Ensure the correct partitions exist to support the specified the boot type.
	switch s.BootType {
	case BootTypeEfi:
		if !espPartitionExists {
			return fmt.Errorf("'esp' partition must be provided for 'efi' boot type")
		}

	case BootTypeLegacy:
		if !biosBootPartitionExists {
			return fmt.Errorf("'bios-grub' partition must be provided for 'legacy' boot type")
		}
	}

	// Ensure all the filesystems objects have an equivalent partition or verity object.
	partitionToFileSystem := make(map[string]*FileSystem)
	verityToFileSystem := make(map[string]*FileSystem)
	for i := range s.FileSystems {
		fileSystem := &s.FileSystems[i]

		partition, foundPartition := partitionSet[fileSystem.DeviceId]
		verity, foundVerity := veritySet[fileSystem.DeviceId]

		switch {
		case foundPartition:
			partitionToFileSystem[fileSystem.DeviceId] = fileSystem
			fileSystem.PartitionId = fileSystem.DeviceId

			if fileSystem.MountPoint != nil && fileSystem.MountPoint.IdType == MountIdentifierTypePartLabel {
				if partition.Label == "" {
					return fmt.Errorf("invalid fileSystem at index %d:\nidType is set to (part-label) but partition (%s) has no label set",
						i, partition.Id)
				}

				labelCount := partitionLabelCounts[partition.Label]
				if labelCount > 1 {
					return fmt.Errorf("invalid fileSystem at index %d:\nmore than one partition has a label of (%s)", i,
						partition.Label)
				}
			}

		case foundVerity:
			verityToFileSystem[fileSystem.DeviceId] = fileSystem
			fileSystem.PartitionId = verity.DataDeviceId

		default:
			return fmt.Errorf("invalid fileSystem at index %d:\nno partition or verity with matching ID (%s)", i,
				fileSystem.DeviceId)
		}
	}

	for _, verity := range s.Verity {
		_, foundHashFileSystem := partitionToFileSystem[verity.HashDeviceId]
		if foundHashFileSystem {
			return fmt.Errorf("a filesystem should not be applied to a verity hash partition (%s)", verity.HashDeviceId)
		}

		dataFileSystem, err := findVerityDataFileSystem(verity, partitionToFileSystem, verityToFileSystem)
		if err != nil {
			return err
		}

		if dataFileSystem.MountPoint != nil && dataFileSystem.MountPoint.IdType != MountIdentifierTypeDefault {
			return fmt.Errorf("filesystem for verity device (%s) may not specify 'mountPoint.idType'",
				dataFileSystem.DeviceId)
		}

		if dataFileSystem.MountPoint == nil || dataFileSystem.MountPoint.Path != "/" {
			return fmt.Errorf("defining secondary verity devices is not currently supported:\n"+
				"filesystems[].mountPoint.path' of verity device (%s) or its data partition (%s) must be set to '/'",
				verity.Id,
				verity.DataDeviceId)
		}

		if verity.Name != VerityRootDeviceName {
			return fmt.Errorf("verity 'name' (%s) must be \"%s\" for filesystem (%s) partition (%s)", verity.Name,
				VerityRootDeviceName, dataFileSystem.MountPoint.Path, verity.DataDeviceId)
		}
	}

	return nil
}

func (s *Storage) CustomizePartitions() bool {
	return len(s.Disks) > 0
}

func findVerityDataFileSystem(verity Verity, partitionToFileSystem map[string]*FileSystem,
	verityToFileSystem map[string]*FileSystem,
) (*FileSystem, error) {
	fileSystem, foundFileSystem := verityToFileSystem[verity.Id]
	dataFileSystem, foundDataFileSystem := partitionToFileSystem[verity.DataDeviceId]
	switch {
	case foundFileSystem && foundDataFileSystem:
		return nil, fmt.Errorf("a filesystem should not be applied to both a verity device (%s) and its data partition (%s)",
			verity.Id, verity.DataDeviceId)

	case foundFileSystem:
		return fileSystem, nil

	case foundDataFileSystem:
		return dataFileSystem, nil

	default:
		return nil, fmt.Errorf("a filesystem was not specified for verity device (%s) or its data partition (%s)",
			verity.Id, verity.DataDeviceId)
	}
}
