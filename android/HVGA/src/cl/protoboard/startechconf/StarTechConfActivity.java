package cl.protoboard.startechconf;

import android.app.Activity;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.WebView;
import android.widget.ImageButton;

public class StarTechConfActivity extends Activity {
	private WebView mWebView;
	private ImageButton back;
	private ImageButton forward;
	private ImageButton refresh;
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
    	super.onCreate(savedInstanceState);
    	setContentView(R.layout.main);
    	mWebView = (WebView) findViewById(R.id.webview);
        mWebView.setVisibility(WebView.INVISIBLE);
        mWebView.getSettings().setJavaScriptEnabled(true);
        mWebView.setWebViewClient(new StarTechConfClient(this));
        mWebView.loadUrl("http://m.startechconf.cl");
        
        back = (ImageButton) findViewById(R.id.btnBack);
        back.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View v) {
				if (mWebView.canGoBack()){
					mWebView.goBack();
				}
			}
		});
        
        forward = (ImageButton) findViewById(R.id.btnForward);
        forward.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View v) {
				if (mWebView.canGoForward()) {
					mWebView.goForward();
				}
			}
		});
        
        refresh = (ImageButton) findViewById(R.id.btnRefresh);
        refresh.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View v) {
				
				findViewById(R.id.relativeLayout1).setVisibility(View.VISIBLE);
				findViewById(R.id.progressBar1).setVisibility(View.VISIBLE);
				mWebView.setVisibility(WebView.VISIBLE);
				
				mWebView.reload();
			}
		});
    }
    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if ((keyCode == KeyEvent.KEYCODE_BACK) && mWebView.canGoBack()) {
            mWebView.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
}