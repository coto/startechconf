package cl.protoboard.startechconf;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;

public class SplashActivity extends Activity {
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.splash);
		Thread splashThread = new Thread() {
			@Override
			public void run() {
				try {
					int waited = 0;
					while (waited < 1000) {
						sleep(100);
						waited += 100;
					}
				} catch (InterruptedException e) {
					// do nothing
				} finally {
					finish();
					Intent i = new Intent();
					i.setClassName("cl.protoboard.startechconf",
							"cl.protoboard.startechconf.StarTechConfActivity");
					startActivity(i);
				}
			}
		};
		splashThread.start();
	}
}
