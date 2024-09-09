import { DefaultAzureCredential } from "@azure/identity";
import { SecretClient } from "@azure/keyvault-secrets";
import {
  BlobSASPermissions,
  BlobServiceClient,
  StorageSharedKeyCredential,
  generateBlobSASQueryParameters,
} from "@azure/storage-blob";

const storageAccountName = process.env.AZURE_STORAGE_ACCOUNT_NAME || "";
const storageAccountKey = process.env.AZURE_STORAGE_ACCOUNT_KEY || "";
const vaultAccountName = process.env.AZURE_VAULT_ACCOUNT_NAME || "";

const credential = new DefaultAzureCredential();
const secretClient = new SecretClient(
  `https://${vaultAccountName}.vault.azure.net`,
  credential
);

const blobServiceClient = new BlobServiceClient(
  `https://${storageAccountName}.blob.core.windows.net`,
  credential
);

const sharedKeyCredential = new StorageSharedKeyCredential(
  `https://${storageAccountName}.blob.core.windows.net`,
  storageAccountKey
);

interface GetBlobUrl {
  containerName: string;
  blobName: string;
}

export const getBlobClient = ({ containerName, blobName }: GetBlobUrl) => {
  const containerClient = blobServiceClient.getContainerClient(containerName);
  const blobClient = containerClient.getBlobClient(blobName);
  return blobClient;
};

export const getBlobUrl = async ({ containerName, blobName }: GetBlobUrl) => {
  const blobClient = getBlobClient({ containerName, blobName });

  // Check if the blob exists
  const exists = await blobClient.exists();
  if (!exists) {
    throw new Error("Blob does not exist");
  }

  const sasToken = generateBlobSASQueryParameters(
    {
      containerName,
      blobName,
      permissions: BlobSASPermissions.parse("r"),
      startsOn: new Date(),
      expiresOn: new Date(new Date().valueOf() + 3600 * 1000), // 1 hour from now
    },
    sharedKeyCredential
  ).toString();

  const blobUrlWithSAS = `${blobClient.url}?${sasToken}`;
  return blobUrlWithSAS;
};
