//
//  AppDelegate.swift
//  Demo app
//
//  Created by Julian Yu-Chung Chen on 4/26/19.
//

import Cocoa

import OTIO_Swift

@NSApplicationMain
class AppDelegate: NSObject, NSApplicationDelegate {



    func applicationDidFinishLaunching(_ aNotification: Notification) {

        NSLog("---> [DEBUG] \(type(of: self)): \(#function)#\(#line): Hello OTIO!")

        let t1 = RationalTime(value: 30.2)
        let t2 = RationalTime(value: 30.2)
        
        NSLog("---> [OTIO] \(type(of: self)): \(#function)#\(#line): times: \(t1) and \(t2)")
    }

    func applicationWillTerminate(_ aNotification: Notification) {
        // Insert code here to tear down your application
    }


}

