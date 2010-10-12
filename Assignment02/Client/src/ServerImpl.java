import java.rmi.server.UnicastRemoteObject;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.rmi.Naming;

import java.util.Timer;
import java.util.TimerTask;

import java.rmi.RemoteException;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * 
 * @author dgourlay
 */
public class ServerImpl extends UnicastRemoteObject implements Server {

	private static final long serialVersionUID = 1;

	private LinkedList<Client> clientList;
	private HashMap<Client, Long> activity;

	private Timer timeoutTimer;
	private final int timeoutSeconds = 10;

	public ServerImpl() throws RemoteException {
		timeoutTimer = new Timer();
		clientList = new LinkedList<Client>();
		activity = new HashMap<Client, Long>();

		timeoutTimer.schedule(new ToDoTask(activity, clientList),
				timeoutSeconds * 1000);

	}

	private class ToDoTask extends TimerTask {
		private HashMap<Client, Long> clientActivity;
		private LinkedList<Client> clientL;

		public ToDoTask(HashMap<Client, Long> h, LinkedList<Client> c) {
			clientActivity = h;
			clientL = c;
		}

		public void run() {

			for (Iterator iter = clientActivity.keySet().iterator(); iter
					.hasNext();) {
				Client key = (Client) iter.next();
				long value = ((Long) clientActivity.get(key)).longValue();

				if((System.currentTimeMillis()- value) > (timeoutSeconds * 1000)){
          clientL.remove(key);
					clientActivity.remove(key);
					try{
					key.setConnected(false);
					key.receive("Timed out, disconnecting...");
					}catch(RemoteException e){
						//do nothing, it is asssumed client is gone
					}
				}
			}

			//timeoutTimer.cancel(); // Terminate the thread
		}
	}

	public synchronized void register(Client c) throws RemoteException {
		clientList.add(c);
		activity.put(c, System.currentTimeMillis());
		c.setConnected(true);

	}

	public synchronized void send_message(String msg, Client c)
			throws RemoteException {

		if (activity.containsKey(c)) {
			activity.remove(c);
			activity.put(c, System.currentTimeMillis());
		} else {
			register(c);
		}

		new MessageRunnable(clientList, c, msg).run();

	}

	public static void main(String[] args) {
		String chat_name;

		try {
			java.rmi.registry.LocateRegistry.createRegistry(1099);
			System.out.println("RMI registry ready.");
		} catch (Exception e) {
			System.out.println("Exception starting RMI registry:");
			e.printStackTrace();
		}

		if (args.length > 0) {
			chat_name = args[0];
		} else {
			chat_name = "Server";
			System.out.println("No chat name arguement passed! Using name: "
					+ chat_name);
		}

		try {
			Naming.rebind(chat_name, new ServerImpl());
		} catch (Exception e) {
			System.out.println("Error Binding Chat Server");
			e.printStackTrace();
		}
	}
}
