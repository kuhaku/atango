var fukidashi, fukidashi2, mmd, koro, last_speech_dt, last_res;
enchant();

var MOTION_PATH = {
  boredom  : 'motion/mei_idle_boredom.vmd',
  think    : 'motion/mei_idle_think.vmd',
  yawn     : 'motion/mei_idle_yawn.vmd',
  laugh    : 'motion/mei_laugh.vmd',
  breath   : 'motion/mei_breath.vmd',
  left     : 'motion/mei_imagine_left_normal.vmd',
  right    : 'motion/mei_imagine_right_normal.vmd',
  greeting : 'motion/sd_mei_greeting.vmd'
};

// 音声認識
var recognition = new webkitSpeechRecognition();
recognition.continuous = true;
recognition.interimResults = true;
recognition.lang = "ja-JP";

// Speech Synthesis
var msg = new SpeechSynthesisUtterance();
msg.volume = 1.0;
msg.rate = 1.0;
msg.pitch = 1.0;
msg.lang = "ja-JP";
msg.voice = speechSynthesis.getVoices().filter(function(voice) { return voice.name == "Google 日本人"; })[0];
last_speech_dt = new Date();
last_res = ""


function get_atango_response(final_transcript){
  koro = mmd.getModelRenderer("korokoro");
  document.getElementById("info").innerText = "へんじをかんがえてます...";

  var think = new MMD.Motion(MOTION_PATH['think']);
  think.load(function() {
    think.loop = true;
    koro.addModelMotion("think", think);
    koro.play("think");
  });

  console.log(final_transcript);
  httpObj = new XMLHttpRequest();
  function speech(httpObj){
    if ((httpObj.readyState == 4) && (httpObj.status == 200)){
      console.log(httpObj.responseText);

      fukidashi2 = new TTweet(700, 64, TTweet.BOTTOM, TTweet.CENTER, 'yellow');
      fukidashi2.x = 150;
      fukidashi2.y = 700;
      fukidashi2.text(httpObj.responseText);
      game.rootScene.addChild(fukidashi2);

      if (last_res != httpObj.responseText){
        msg.text = httpObj.responseText;
        window.speechSynthesis.speak(msg);
        cnt++;
        last_res = httpObj.responseText;
      }

      document.getElementById("utterance").innerText = cnt;
      document.getElementById("info").innerText = "もっとはなそう！";
      var yawn = new MMD.Motion(MOTION_PATH['yawn']);
      yawn.load(function() {
        yawn.loop = true;
        koro.addModelMotion("yawn", yawn);
        koro.play("yawn");
      });
    } else{
      var laugh = new MMD.Motion(MOTION_PATH['laugh']);
      laugh.load(function() {
        laugh.loop = true;
        koro.addModelMotion("laugh", laugh);
        koro.play("laugh");
      });
    }
  }
  httpObj.onreadystatechange = function(){speech(httpObj);};
  if (httpObj){
      url = 'http://mamisan.no-ip.org/api/dialogue/?text='+final_transcript;
    httpObj.open("GET", url, true);
    httpObj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    httpObj.send();
  }
}

recognition.onresult = function(event) {
  var length = event.results.length;
  var intermediate_transcript ="";
  var final_transcript = "";
  console.log(length);
  if (length > 0) {
    for (var i = event.resultIndex; i < event.results.length; i++){
      var recogStr = event.results[i][0].transcript;
      intermediate_transcript += recogStr;
      remove_fukidashi();
    fukidashi = new TTweet(650, 64, TTweet.BOTTOM, TTweet.CENTER, 'white');
      fukidashi.text(intermediate_transcript);
      fukidashi.x = 150;
      fukidashi.y = 10;
      game.rootScene.addChild(fukidashi);
      setTimeout(remove_fukidashi(), 5000);
      //認識の最終結果
      if (event.results[i].isFinal || i == event.results.length){
        if (recogStr == ' うー') {
            console.log('noise');
            return;
        }
        final_transcript += recogStr
      }
    }
    if (final_transcript.length > 1){
      remove_fukidashi();
      fukidashi = new TTweet(650, 64, TTweet.BOTTOM, TTweet.CENTER, 'white');
      fukidashi.x = 150;
      fukidashi.y = 10;
      fukidashi.text(final_transcript);
      game.rootScene.addChild(fukidashi);
      setTimeout(remove_fukidashi(), 5000);

      now_dt = new Date();
      if ((now_dt.getTime() - last_speech_dt.getTime()) > 3){
        get_atango_response(final_transcript);
      }
    }
    else {
      document.getElementById("info").innerText = "にんしきちゅう...";
      koro = mmd.getModelRenderer("korokoro");
      var think = new MMD.Motion(MOTION_PATH['think']);
      think.load(function() {
        think.loop = true;
      koro.addModelMotion("think", think);
        koro.play("think");
      });
    }
  }
};

recognition.onstart = function(event) {
    document.getElementById("info").innerText = "ぁたんごちゃんとはなそう！";
    koro = mmd.getModelRenderer("korokoro");
    var boredom = new MMD.Motion(MOTION_PATH['boredom']);
    boredom.load(function() {
        boredom.loop = true;
      koro.addModelMotion("boredom", boredom);
        koro.play("boredom");
    });
};

recognition.onspeechstart = function(event) {
    document.getElementById("info").innerText = "にんしきちゅう...";
  koro = mmd.getModelRenderer("korokoro");
    var think = new MMD.Motion(MOTION_PATH['think']);
    think.load(function() {
        think.loop = true;
      koro.addModelMotion("think", think);
        koro.play("think");
    });
};

recognition.onnomatch = function(){
    document.getElementById("info").innerText = "ききとれなかったよ！";
};

recognition.onerror = function(){
    document.getElementById("info").innerText = "エラー";
};

recognition.onend = function(){
    document.getElementById("info").innerText = "またはなそう？";
    recognition.start();
};
var cnt = 0;
recognition.start();

window.onload = function() {
  game = new Game(1000, 1000);
  game.onload = function() {
    var scene = new Scene3D();
  var camera = scene.getCamera();
  camera.y = 20;
  camera.z = 80;
  camera.centerY = 10;

    var canvas = document.getElementsByTagName('canvas')[0];
    mmd = new MMD(canvas, canvas.width, canvas.height);
    mmd.registerKeyListener(canvas);
    mmd.registerMouseListener(canvas);

    mmd.addModel("korokoro", new MMD.Model('model/korokoro', 'korokoro.pmd'));

    mmd.load(function() {
      var koro = mmd.getModelRenderer("korokoro");
      koro.translate(0, 6, 0.0);

      var greet = new MMD.Motion(MOTION_PATH['greeting']);
      greet.load(function() {
        greet.loop = false;
        koro.addModelMotion("greeting", greet);
        koro.play("greeting");
      });

      mmd.start();
      mmd.play();
    });
    game.rootScene.addChild(mmd);

    var oldX = 0;
    r = Math.PI / 2;

    game.rootScene.addEventListener('touchstart', function(e) {
        oldX = e.x;
    });
    game.rootScene.addEventListener('touchmove', function(e) {
      r += (e.x - oldX) / 100;
      camera.x = Math.cos(r) * 80;
      camera.z = Math.sin(r) * 80;
      oldX = e.x;
    });

    var label = new Label('0');
    label.font = '24px helvetica';
    label.color = '#fff';
    game.rootScene.addChild(label);
    var c = 0;
    setInterval(function() {
      label.text = c;
      c = 0;
    }, 1000);
    game.rootScene.addEventListener('enterframe', function(e) {
        c++;
    });
  };
  game.start(); //ゲーム開始
};


// ふきだしクラス
// Ref: http://v416.hateblo.jp/entry/2012/10/19/225500
TTweet = enchant.Class.create(enchant.Sprite, {
  initialize : function(w, h, line, align, color) {
    enchant.Sprite.call(this, w, h + TTweet.TAIL);
    this.line = line;
    this.align = align;
    this.image = new Surface(w, h + TTweet.TAIL);
    this.liner = new Surface(w, h);
    var t = TTweet.TAIL;
    var s = TTweet.SIZE;
    var c = TTweet.CURVE;
    this.outCurve = {
      lt : {x:0, y:0},
      rt : {x:w, y:0},
      rd : {x:w, y:h},
      ld : {x:0, y:h}
    };
    this.inCurve = {
      lt : {x:0+s, y:0+s},
      rt : {x:w-s, y:0+s},
      rd : {x:w-s, y:h-s},
      ld : {x:0+s, y:h-s}
    };
    var o = this.outCurve;
    var i = this.inCurve;

    with(this.liner.context) {
      fillStyle = '#aaaaaa';
      strokeStyle = '#aaaaa';
      beginPath();
      moveTo(o.lt.x, o.lt.y+c);
      quadraticCurveTo(o.lt.x, o.lt.y, o.lt.x+c, o.lt.y);
      lineTo(o.rt.x-c, o.rt.y);
      quadraticCurveTo(o.rt.x, o.rt.y, o.rt.x, o.rt.y+c);
      lineTo(o.rd.x, o.rd.y-c);
      quadraticCurveTo(o.rd.x, o.rd.y, o.rd.x-c, o.rd.y);
      lineTo(o.ld.x+c, o.ld.y);
      quadraticCurveTo(o.ld.x, o.ld.y, o.ld.x, o.ld.y-c);
      closePath();
      fill();
      stroke();
      // 抜く
      fillStyle = color;
      beginPath();
      moveTo(i.lt.x, o.lt.y+c);
      quadraticCurveTo(i.lt.x, i.lt.y, o.lt.x+c, i.lt.y);
      lineTo(o.rt.x-c, i.rt.y);
      quadraticCurveTo(i.rt.x, i.rt.y, i.rt.x, o.rt.y+c);
      lineTo(i.rd.x, o.rd.y-c);
      quadraticCurveTo(i.rd.x, i.rd.y, o.rd.x-c, i.rd.y);
      lineTo(o.ld.x+c, i.ld.y);
      quadraticCurveTo(i.ld.x, i.ld.y, i.ld.x, o.ld.y-c);
      closePath();
      fill();
    };
    // しっぽ
    var b = {
      x:this.align==TTweet.LEFT ?TTweet.HORN:
        this.align==TTweet.RIGHT?this.width-TTweet.HORN:this.width/2,
      y:this.line==TTweet.TOP?0:this.height
    };
    var triangle = {
      c:{x:b.x  ,y:b.y},
      l:{x:b.x-TTweet.TAIL/2,y:b.y+(this.line==TTweet.TOP?1:-1)*TTweet.TAIL},
      r:{x:b.x+TTweet.TAIL/2,y:b.y+(this.line==TTweet.TOP?1:-1)*TTweet.TAIL}
    };
    with(this.image.context) {
      fillStyle = '#aaaaaa';
      strokeStyle = '#aaaaaa';
      beginPath();
      moveTo(triangle.l.x,triangle.l.y);
      lineTo(triangle.c.x,triangle.c.y);
      lineTo(triangle.r.x,triangle.r.y);
      closePath();
      fill();
      stroke();
    };
    //this.clear();
  },
  clear : function() {
    this.image.draw(this.liner, 0, this.line == TTweet.TOP ? TTweet.TAIL : 0);
  },
  text : function(text) {
    this.clear();
    with(this.image.context) {
      font = 'bold 24px メイリオ';
      fillStyle = '#666666';
      textAlign = 'center';
      textBaseline = 'middle';
      fillText(text,this.width/2,this.height/2 - (this.line==TTweet.TOP?0:TTweet.TAIL));
    };
  }
});
TTweet.TAIL   =  0;
TTweet.SIZE   =  2;
TTweet.CURVE  = 16;
TTweet.HORN   = 16;
TTweet.TOP    = "top";
TTweet.BOTTOM = "bottom";
TTweet.CENTER = "center";
TTweet.LEFT   = "left";
TTweet.RIGHT  = "right";

function remove_fukidashi(){
  if (fukidashi){
    fukidashi.remove();
    fukidashi = null;
  }
  if (fukidashi2){
    fukidashi2.remove();
    fukidashi2 = null;
  }
}
