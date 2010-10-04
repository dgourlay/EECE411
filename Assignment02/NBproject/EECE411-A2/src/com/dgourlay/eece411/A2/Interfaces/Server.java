/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package com.dgourlay.eece411.A2.Interfaces;

import java.rmi.Remote;
import java.rmi.RemoteException;

/**
 *
 * @author dgourlay
 */
public interface Server extends Remote {

    void register(Client c) throws RemoteException;

    void send_message(String s) throws RemoteException;
}
