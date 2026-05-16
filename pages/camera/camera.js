// pages/camera/camera.js
const app=getApp()
const API_BASE=app.API_BASE||'http://121.41.20.177:8000';
Page({

  /**
   * 页面的初始数据
   */
  data: {
    recordId:0,
    showPreview:false,
    tempImagePath:''

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    this.setData({
      recordId:options.recordId||0
    })

  },
  //------------1拍照-----------------
  takePhoto(){
  const cxt=wx.createCameraContext();
  cxt.takePhoto({
    quality:'high',
    success:(res)=>{
    //--------------2拍照成功，进入预览模式--------
     this.setData({
      showPreview:true,
      tempImagePath:res.tempImagePath,
     })
    },
    fail:()=>{
      wx.showToast({title:'网络错误',icon:'none'})
    }
  })
  },


  //-------------3如果取消那就重新进入拍照模式--------------
  retakePhoto(){
  this.setData({
    showPreview:false,
    tempImagePath:'',
  })
  },


  //--------------4确定就合成水印照片--------------
  confirmPhoto(){
  wx.showLoading({title:'处理中...'});
  this.addWaterMark(this.data.tempImagePath);
  },


  //--------------5添加水印----------------------
  addWaterMark(imagePath){
    const that = this;
    // 学生信息
    const userInfo = {
      name: wx.getStorageSync('name') || '学生',
      student_id: wx.getStorageSync('student_id') || ''
    };
    // 时间
    const now = new Date();
    const dateStr = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()} ${now.getHours()}:${now.getMinutes()}`;
    // 获取 Canvas 节点
    const query = wx.createSelectorQuery();
    query.select('#watermarkCanvas')
      .fields({ node: true, size: true })
      .exec((res) => {
        if (!res[0]) {
          wx.hideLoading();
          wx.showToast({ title: 'Canvas 节点获取失败', icon: 'none' });
          return;
        }
        const canvas = res[0].node;
        const ctx = canvas.getContext('2d');
        // 创建图片对象
        const img = canvas.createImage();
        img.src = imagePath;
        img.onload = () => {
          canvas.width = img.width;
          canvas.height = img.height;
          // 绘制原图
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          // 绘制水印文字
          ctx.fillStyle = 'white';
          ctx.font = 'bold 30px sans-serif';
          ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
          ctx.shadowBlur = 10;
          ctx.shadowOffsetX = 5;
          ctx.shadowOffsetY = 5;
          ctx.fillText(`${userInfo.name}(${userInfo.student_id})`, 20, canvas.height - 100);
          ctx.fillText(`打卡时间: ${dateStr}`, 20, canvas.height - 60);
          ctx.fillText(`打扫状态: 已打扫`, 20, canvas.height - 20);
          // 导出图片
          wx.canvasToTempFilePath({
            canvas: canvas,
            success: (res) => {
              that.uploadImage(res.tempFilePath);
            },
            fail: (err) => {
              wx.hideLoading();
              console.error('导出水印照片失败', err);
              wx.showToast({ title: '合成水印失败', icon: 'none' });
            }
          }, that);
        };
        img.onerror = (err) => {
          wx.hideLoading();
          console.error('图片加载失败', err);
          wx.showToast({ title: '图片加载失败', icon: 'none' });
        };
      });
  },
  //------------------5上传水印照片----------
  uploadImage(WaterMarkPath){
   const token=wx.getStorageSync('token');
   wx.uploadFile({
    filePath:WaterMarkPath,
    name:'file',
      
    url:`${API_BASE}/upload/upload_watermark`,
    success:(res)=>{
       try {
         const data=JSON.parse(res.data);//先把数据转换成JSON格式
         const photoUrl=data.url||data.data||res.data;
         const base64=data.base64||''
         this.submitCheckIn(photoUrl, base64);//把照片路径和照片的二进制文字格式提交上传
       }
       catch(e){
        wx.hideLoading()
        wx.showToast({title:'上传失败',icon:'none'})
       }
    },
    fail:()=>{
      wx.hideLoading();
      wx.showToast({ title: '上传失败', icon: 'none' });
    }
   })
  },

  //---------------6提交上传------------
  submitCheckIn(photo, base64){
    const token=wx.getStorageSync('token');
    wx.request({
      method:'POST',
      url: `${API_BASE}/duty/submit_watermark`,
      header:{ 'Authorization': `Bearer ${token}` },
      data:{
        watermark_url:photo,
        record_id:this.data.recordId,
        base64_data:base64||'',
      },
      success:(res)=>{
        wx.hideLoading();
        if(res.statusCode==200){
          wx.showToast({ title: '打卡成功', icon: 'success' });
          //通知任务首页更新
          const pages=getCurrentPages();
          const prepage=pages[pages.length-2];
          //把任务首页的检查给设置为true
          if(prepage){
           prepage.setData({isCheckedIn: true});
           prepage.fetchTodayTask();
          }
          //返回学生任务首页
          setTimeout(()=>wx.navigateBack(),1500);
  
        }
        else{
          wx.showToast({ title: '打卡失败', icon: 'none' });
        }
      },
      fail: () => {
        wx.hideLoading();
        wx.showToast({ title: '网络错误', icon: 'none' })
      }
      
    })
  },




  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  }
})