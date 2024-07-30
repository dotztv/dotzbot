const { SlashCommandBuilder } = require('discord.js');
const net = require('net');
const config = require('../../config.json');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('zhermito')
    .setDescription('Tries to start ZHermito'),
  async execute(interaction) {
    // Reply to the user to acknowledge the command execution
    await interaction.reply('Trying to send message to start server, look for status in #mc-chat\n If the server isnt started within 2 minutes, it\'s safe to assume that dotz\'s pc is not online.');
    console.log("Zhermito command received by " + interaction.user)

    // Create a TCP client and connect to the server
    const client = new net.Socket();
    const HOST = config.SERVER_IP;  // Fetch server IP from config
    const PORT = config.SERVER_PORT || 3000;  // Fetch server port from config or use default

    client.connect(PORT, HOST, () => {
      // Send the specific message to the server
      client.write('zhermito');
      // Disconnect after sending the message
      client.end();
    });
  },
};
