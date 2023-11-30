const {
  SecretsManagerClient,
  GetSecretValueCommand,
} = require('@aws-sdk/client-secrets-manager');

const region = 'us-east-1';

async function getConnection(secretName) {
  const client = new SecretsManagerClient({
    region,
  });

  response = await client.send(
    new GetSecretValueCommand({
      SecretId: secretName,
    })
  );

  const secret = response.SecretString;
  return (JSON.parse(secret));
}

module.exports = getConnection;
