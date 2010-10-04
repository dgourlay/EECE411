import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;

public class ClientImpl extends UnicastRemoteObject implements Client, Runnable {

	static GUI gui;
	static MessageQueue _queue;
	private Server srv;

	public ClientImpl(Server srv) throws RemoteException {
		this.srv = srv;
		srv.register(this);

		// create a shared buffer where the GUI add the messages thet need to
		// be sent out by the main thread. The main thread stays in a loop
		// and when a new message shows up in the buffer it sends it out
		// to the chat server (using RMI)

		_queue = new MessageQueue();

		// instantiate the GUI - in a new thread
		javax.swing.SwingUtilities.invokeLater(new Runnable() {

			public void run() {
				gui = GUI.createAndShowGUI(_queue);
			}
		});

		// hack make sure the GUI instantioation is completed by the GUI thread
		// before the next call
		while (gui == null) {
			Thread.currentThread().yield();
		}

		// calling the GUI method that updates the text area of the GUI
		// NOTE: you might want to call the same method when a new chat message
		// arrives
		gui.addToTextArea("Welcome to the EECE411-A2 Chat Program!");

	}

	public synchronized void receive(String s) throws RemoteException {
		System.out.println("Message Received: " + s);
		gui.addToTextArea("RemoteUser:> " + s);
	}

	public void run() {

		// The code below serves as an example to show how the shares message
		// between the GUI and the main thread.
		// You will probably want to replace the code below with code that sits
		// in a loop,
		// waits for new messages to be entered by the user, and sends them to
		// the
		// chat server (using an RMI call)
		//
		// In addition you may want to add code that
		// * connects to the chat server and provides an object for callbacks
		// (so
		// that the server has a way to send messages generated by other users)
		// * implement the callback object which is called by the server
		// remotely
		// and, in turn, updates the local GUI

		while (true) {

			String s;
			try {
				// wait until the user enters a new chat message
				s = _queue.dequeue();
			} catch (InterruptedException ie) {
				break;
			}

			try {

				// update the GUI with the message entered by the user
				gui.addToTextArea("Me:> " + s);
				srv.send_message(s, this);
				System.out.println("Sending message to server: " + s);

			} catch (Exception e) {
				System.out.println("System error!");
				e.printStackTrace();
			}

		} // end while loop

	}

	public static void main(String[] args) {
		String url = "rmi://localhost/Server";
		// String url = args[0];

		try {
			Server chat_server = (Server) Naming.lookup(url);
			new Thread(new ClientImpl(chat_server)).start();
		} catch (Exception e) {
			System.out.println("Client error encountered");
			e.printStackTrace();
		}
	}
}
