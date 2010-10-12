
import java.rmi.RemoteException;

import java.util.LinkedList;

class MessageRunnable implements Runnable {

	private LinkedList<Client> clientList;
	private Client c;
	private String msg;

	public MessageRunnable(LinkedList<Client> clientList, Client c, String msg) {
     this.clientList = clientList;
		 this.c = c;
		 this.msg = msg;

	}

	public void run() {
		System.out.println("Message rcvd... " + msg);
		for (Client cs : clientList) {
			if (!cs.equals(c)) {
				try{
				cs.receive(msg);
				}catch(RemoteException e){
					e.printStackTrace();
				}
			}
		}
	}

}
