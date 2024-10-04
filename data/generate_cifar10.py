import torch
import torchvision
import argparse
import pathlib

def fetch_dataset(do_download, data_path):
    transform_train = torchvision.transforms.Compose([
        torchvision.transforms.RandomCrop(32, padding=4),
        torchvision.transforms.RandomHorizontalFlip(),
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    transform_test = torchvision.transforms.Compose([
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])
    
    # Emulate a system call inside Gramine, which degrades performance
    train_data = torchvision.datasets.CIFAR10(
        data_path, train=True, download=do_download, transform=transform_train
    )
    test_data = torchvision.datasets.CIFAR10(
        data_path, train=False, download=do_download, transform=transform_test
    )

    print("There are {train_size} samples for training".format(train_size=len(train_data)))
    print("There are {test_size} samples for testing in the server".format(test_size=len(test_data)))

    return train_data, test_data

def iid_partition_loader(data, bsz=4, n_clients=20, train_fraction=0.8):
    m = len(data)
    assert m % n_clients == 0 # Must be divisible
    m_per_client = m // n_clients 
    assert m_per_client % bsz == 0
    assert train_fraction < 1
    test_fraction = 1-train_fraction
    print("There are {n} clients".format(n=n_clients))
    print("Each client can use {n} samples".format(n=m_per_client))
    
    clients_data = torch.utils.data.random_split(
        data,
        [m_per_client for x in range(n_clients)]
    )

    clients_trainloader = []
    clients_testloader = []
    for client_data in clients_data:
        client_trainset, client_testset = torch.utils.data.random_split(client_data, [train_fraction, test_fraction])
        client_trainloader = torch.utils.data.DataLoader(client_trainset, batch_size=bsz, shuffle=True)
        client_testloader = torch.utils.data.DataLoader(client_testset, batch_size=bsz, shuffle=True)
        clients_trainloader.append(client_trainloader)
        clients_testloader.append(client_testloader)

    print("Each client has a trainloader with batch size {} and {} samples".format(bsz, round(train_fraction*m_per_client)))
    print("Each client has a testloader with batch size {} and {} samples".format(bsz, round(m_per_client-train_fraction*m_per_client)))

    return clients_trainloader, clients_testloader


def generate_data(
    do_download,
    data_path,
    private_data_path,
    public_data_path,
    train_batch_size,
    test_batch_size,
    num_partitions,
    num_used_clients,
    train_fraction
):
    train_data, test_data = fetch_dataset(do_download, data_path)
    
    train_loaders_list, local_test_loaders_list = iid_partition_loader(
        train_data, bsz=train_batch_size, n_clients=num_partitions, train_fraction=train_fraction) # NUM_CLIENTS=10
    for i, train_loader in enumerate(train_loaders_list[:num_used_clients]):
        torch.save(train_loader,"{p}/client_{i}_trainloader.pth".format(i=i,p=private_data_path))
    for i, test_loader in enumerate(local_test_loaders_list[:num_used_clients]):
        torch.save(test_loader,"{p}/client_{i}_testloader.pth".format(i=i,p=private_data_path))
    global_test_loader = torch.utils.data.DataLoader(test_data, batch_size = test_batch_size, shuffle=False)
    torch.save(global_test_loader, "{p}/server_testloader.pth".format(p=public_data_path))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare CIFAR10 batches")
    parser.add_argument('--num_partitions', type=int, help='Number of partitions (integer)', required=True)
    parser.add_argument('--num_used_clients', type=int, help='Number of used clients (integer)', required=True)
    parser.add_argument('--train_batch_size', type=int, help='Training batch size (integer)', required=True)
    parser.add_argument('--server_test_batch_size', type=int, help='Testing batch size for server (integer)', required=True)
    parser.add_argument('--train_fraction', type=float, help='Percentage of data for training (float)', required=True)
    parser.add_argument('--download', action='store_true', help='Download dataset from the Internet')
    args = parser.parse_args()
    
    base_path = str(pathlib.Path().resolve())
    data_path = base_path + "/CIFAR10"
    public_data_path = base_path + "/CIFAR10/public_dataloaders"
    private_data_path = base_path + "/CIFAR10/private_dataloaders_clear"
    do_download = args.download

    generate_data(
        do_download,
        data_path,
        private_data_path,
        public_data_path,
        args.train_batch_size,
        args.server_test_batch_size,
        args.num_partitions,
        args.num_used_clients,
        args.train_fraction
    )