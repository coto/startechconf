package cl.protoboard.startechconf;

import android.content.Intent;
import android.net.Uri;
import android.view.View;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class StarTechConfClient extends WebViewClient {
	StarTechConfActivity viewActivity;
	public StarTechConfClient(StarTechConfActivity starTechConfActivity) {
		viewActivity = starTechConfActivity;
	}

	@Override
    public boolean shouldOverrideUrlLoading(WebView view, String url) {
		if (url.startsWith("mailto:") || url.startsWith("geo:") || url.startsWith("tel:")) {
			Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
			viewActivity.startActivity(intent);
		} else {
			view.loadUrl(url);
		}
        return true;
    }
	@Override
	public void onPageFinished(WebView view, String url) {
		super.onPageFinished(view, url);
		viewActivity.findViewById(R.id.relativeLayout1).setVisibility(View.GONE);
		viewActivity.findViewById(R.id.progressBar1).setVisibility(View.GONE);
		view.setVisibility(WebView.VISIBLE);
	}
}
