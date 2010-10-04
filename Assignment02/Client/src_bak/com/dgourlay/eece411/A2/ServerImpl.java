/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package com.dgourlay.eece411.A2;

import com.dgourlay.eece411.A2.Interfaces.*;

import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.util.LinkedList;

/**
 *
 * @author dgourlay
 */
public class ServerImpl extends UnicastRemoteObject implements Server {

    private LinkedList<Client> clientList;

    public ServerImpl() throws RemoteException {
        clientList = new LinkedList<Client>();

    }

    public synchronized void register(Client c) throws RemoteException {
        clientList.add(c);
    }

    public synchronized void send_message(String s) throws RemoteException {
        for (int i = 0; i < clientList.size(); i++) {
            clientList.get(i).receive(s);
        }
    }

    public static void main(String[] args) {
        try {
            Naming.rebind("Server", new ServerImpl());
        } catch (Exception e) {
            System.out.println("Error Binding");
            e.printStackTrace();
        }
    }
}
